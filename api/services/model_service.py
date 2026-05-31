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

    def load(self):
        """Load model from checkpoint."""
        self.model = create_model(pretrained=False)
        checkpoint = torch.load(CHECKPOINT_PATH, map_location=self.device, weights_only=True)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()
        self.transform = get_val_transforms(IMAGE_SIZE)
        print(f"Model loaded on {self.device}")

    def predict(self, image: Image.Image) -> dict:
        """Run prediction on a PIL Image."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.model(input_tensor)

        calories, fat, carb, protein = output[0].cpu().numpy()
        return {
            "calories": round(float(calories), 1),
            "fat_g": round(float(fat), 2),
            "carb_g": round(float(carb), 2),
            "protein_g": round(float(protein), 2),
        }

    @property
    def is_loaded(self) -> bool:
        return self.model is not None


# Singleton instance
_model_service = ModelService()


def get_model_service() -> ModelService:
    return _model_service
