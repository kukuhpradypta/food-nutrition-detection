"""
Dataset class for food nutrition regression.
Loads images and returns nutrition targets (calories, fat, carb, protein).
"""
import os
import torch
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


def get_train_transforms(image_size=224):
    """Augmentation transforms for training."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])


def get_val_transforms(image_size=224):
    """Transforms for validation/inference (no augmentation)."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])


class FoodNutritionDataset(Dataset):
    """
    Dataset for food nutrition prediction.
    Returns image tensor and target tensor [calories, fat, carb, protein].
    """

    # Target columns in order
    TARGET_COLS = ["total_calories", "total_fat", "total_carb", "total_protein"]

    def __init__(self, csv_file, image_dir, transform=None):
        self.df = pd.read_csv(csv_file)
        self.image_dir = image_dir
        self.transform = transform

        # Pre-compute target statistics for normalization
        self.target_mean = self.df[self.TARGET_COLS].mean().values
        self.target_std = self.df[self.TARGET_COLS].std().values

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        # Load image
        image_path = os.path.join(self.image_dir, row["image"])
        image = Image.open(image_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        # Target: [calories, fat, carb, protein]
        targets = torch.tensor(
            [row[col] for col in self.TARGET_COLS],
            dtype=torch.float32
        )

        return image, targets

    def get_target_stats(self):
        """Return mean and std of targets for normalization."""
        return (
            torch.tensor(self.target_mean, dtype=torch.float32),
            torch.tensor(self.target_std, dtype=torch.float32),
        )
