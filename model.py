"""
Model definition: MobileNetV2 for nutrition regression.
Outputs 4 values: [calories, fat, carb, protein]
"""
import torch
import torch.nn as nn
from torchvision import models


class FoodNutritionModel(nn.Module):
    """
    MobileNetV2-based regression model for predicting food nutrition.
    Chosen for mobile deployment (small, fast, efficient).
    """

    def __init__(self, num_outputs=4, pretrained=True):
        super().__init__()

        # Load pretrained MobileNetV2
        weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        self.backbone = models.mobilenet_v2(weights=weights)

        # Replace classifier head for regression
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(256, num_outputs),
            # No activation: model predicts normalized targets (can be negative).
            # Values are denormalized and clamped to >= 0 at inference time.
        )

    def forward(self, x):
        return self.backbone(x)


def create_model(pretrained=True):
    """Factory function to create the model."""
    model = FoodNutritionModel(num_outputs=4, pretrained=pretrained)
    return model
