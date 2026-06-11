"""
Model service - handles ML model loading and inference.
"""
import torch
from PIL import Image

from api.config import CHECKPOINT_PATH, IMAGE_SIZE

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_transform import get_val_transforms
from model import create_model


class ModelService:
    """Singleton service for ML model inference."""

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = None
        self.target_mean = None
        self.target_std = None

    def load(self):
        """Load model from checkpoint."""
        self.model = create_model(pretrained=False)
        checkpoint = torch.load(CHECKPOINT_PATH, map_location=self.device, weights_only=True)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()
        self.transform = get_val_transforms(IMAGE_SIZE)

        # Load normalization stats (fallback to identity if missing)
        self.target_mean = checkpoint.get("target_mean")
        self.target_std = checkpoint.get("target_std")
        if self.target_mean is not None:
            self.target_mean = self.target_mean.to(self.device)
            self.target_std = self.target_std.to(self.device)

        print(f"Model loaded on {self.device}")

    def predict(self, image: Image.Image) -> dict:
        """
        Run prediction on a PIL Image.
        Uses Monte Carlo Dropout (N forward passes with dropout active)
        to estimate prediction confidence.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        MC_SAMPLES = 20  # number of stochastic forward passes

        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # Enable dropout during inference for MC sampling
        self.model.train()
        outputs = []
        with torch.no_grad():
            for _ in range(MC_SAMPLES):
                out = self.model(input_tensor)[0]
                if self.target_mean is not None:
                    out = out * self.target_std + self.target_mean
                out = torch.clamp(out, min=0.0)
                outputs.append(out.cpu())
        self.model.eval()

        # Stack: shape [MC_SAMPLES, 4]
        stacked = torch.stack(outputs)
        mean_pred = stacked.mean(dim=0)
        std_pred  = stacked.std(dim=0)

        calories, fat, carb, protein = mean_pred.numpy()
        std_cal, std_fat, std_carb, std_pro = std_pred.numpy()

        # Confidence: coefficient of variation (lower = more confident)
        # confidence_score: 0-100, higher = more confident
        def confidence(mean_val, std_val):
            if mean_val == 0:
                return 100.0
            cv = std_val / (mean_val + 1e-6)  # coefficient of variation
            # Map: cv=0 → 100%, cv=0.5+ → 0%
            score = max(0.0, (1.0 - cv * 2.0)) * 100
            return round(float(score), 1)

        conf_calories = confidence(calories, std_cal)
        conf_fat      = confidence(fat, std_fat)
        conf_carb     = confidence(carb, std_carb)
        conf_protein  = confidence(protein, std_pro)
        overall_conf  = round((conf_calories + conf_fat + conf_carb + conf_protein) / 4, 1)

        # Threshold label
        if overall_conf >= 70:
            confidence_label = "high"
        elif overall_conf >= 40:
            confidence_label = "medium"
        else:
            confidence_label = "low"

        return {
            "calories": round(float(calories), 1),
            "fat_g":    round(float(fat), 2),
            "carb_g":   round(float(carb), 2),
            "protein_g": round(float(protein), 2),
            "confidence": {
                "overall_score": overall_conf,
                "level": confidence_label,
                "detail": {
                    "calories": conf_calories,
                    "fat_g":    conf_fat,
                    "carb_g":   conf_carb,
                    "protein_g": conf_protein,
                }
            }
        }

    @property
    def is_loaded(self) -> bool:
        return self.model is not None


# Singleton instance
_model_service = ModelService()


def get_model_service() -> ModelService:
    return _model_service
