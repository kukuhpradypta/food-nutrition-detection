"""
Training script for food nutrition prediction model.
Trains MobileNetV2 to predict calories, fat, carb, protein from food images.

Usage:
    python data_training.py
"""
import os
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import CosineAnnealingLR

from data_transform import FoodNutritionDataset, get_train_transforms, get_val_transforms
from model import create_model

# ============ Configuration ============
CONFIG = {
    "image_dir": "image_resource",
    "train_csv": "data/train.csv",
    "val_csv": "data/val.csv",
    "output_dir": "checkpoints",
    "image_size": 224,
    "batch_size": 32,
    "num_epochs": 50,
    "learning_rate": 1e-3,
    "weight_decay": 1e-4,
    "num_workers": 2,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch, return average loss."""
    model.train()
    total_loss = 0.0
    num_batches = 0

    for images, targets in dataloader:
        images = images.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()
        predictions = model(images)
        loss = criterion(predictions, targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches


def validate(model, dataloader, criterion, device):
    """Validate model, return average loss and per-target MAE."""
    model.eval()
    total_loss = 0.0
    total_mae = torch.zeros(4)
    num_batches = 0
    num_samples = 0

    with torch.no_grad():
        for images, targets in dataloader:
            images = images.to(device)
            targets = targets.to(device)

            predictions = model(images)
            loss = criterion(predictions, targets)

            total_loss += loss.item()
            # MAE per target
            mae = torch.abs(predictions - targets).sum(dim=0).cpu()
            total_mae += mae
            num_batches += 1
            num_samples += images.size(0)

    avg_loss = total_loss / num_batches
    avg_mae = total_mae / num_samples

    return avg_loss, avg_mae


def main():
    cfg = CONFIG
    os.makedirs(cfg["output_dir"], exist_ok=True)
    device = torch.device(cfg["device"])
    print(f"Using device: {device}")

    # ---- Data ----
    train_transform = get_train_transforms(cfg["image_size"])
    val_transform = get_val_transforms(cfg["image_size"])

    train_dataset = FoodNutritionDataset(
        cfg["train_csv"], cfg["image_dir"], transform=train_transform
    )
    val_dataset = FoodNutritionDataset(
        cfg["val_csv"], cfg["image_dir"], transform=val_transform
    )

    train_loader = DataLoader(
        train_dataset, batch_size=cfg["batch_size"],
        shuffle=True, num_workers=cfg["num_workers"], pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=cfg["batch_size"],
        shuffle=False, num_workers=cfg["num_workers"], pin_memory=True
    )

    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")

    # ---- Model ----
    model = create_model(pretrained=True).to(device)

    # Freeze backbone initially for first 5 epochs (transfer learning)
    for param in model.backbone.features.parameters():
        param.requires_grad = False

    # ---- Loss & Optimizer ----
    criterion = nn.MSELoss()
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=cfg["learning_rate"],
        weight_decay=cfg["weight_decay"],
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg["num_epochs"])

    # ---- Training Loop ----
    best_val_loss = float("inf")
    target_names = ["Calories", "Fat", "Carb", "Protein"]

    print("\n" + "=" * 60)
    print("Starting training...")
    print("=" * 60)

    for epoch in range(cfg["num_epochs"]):
        start_time = time.time()

        # Unfreeze backbone after epoch 5
        if epoch == 5:
            print("\n>> Unfreezing backbone layers...")
            for param in model.backbone.features.parameters():
                param.requires_grad = True
            # Reset optimizer with all parameters
            optimizer = torch.optim.AdamW(
                model.parameters(),
                lr=cfg["learning_rate"] * 0.1,  # Lower LR for fine-tuning
                weight_decay=cfg["weight_decay"],
            )
            scheduler = CosineAnnealingLR(optimizer, T_max=cfg["num_epochs"] - 5)

        # Train
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device)

        # Validate
        val_loss, val_mae = validate(model, val_loader, criterion, device)

        scheduler.step()

        elapsed = time.time() - start_time

        # Print progress
        print(f"\nEpoch [{epoch+1}/{cfg['num_epochs']}] ({elapsed:.1f}s)")
        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Val Loss:   {val_loss:.4f}")
        print(f"  Val MAE:    ", end="")
        for name, mae_val in zip(target_names, val_mae):
            print(f"{name}={mae_val:.2f}  ", end="")
        print()

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            save_path = os.path.join(cfg["output_dir"], "best_model.pth")
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_loss,
                "val_mae": val_mae,
            }, save_path)
            print(f"  >> Saved best model (val_loss={val_loss:.4f})")

    # Save final model
    final_path = os.path.join(cfg["output_dir"], "final_model.pth")
    torch.save({
        "epoch": cfg["num_epochs"],
        "model_state_dict": model.state_dict(),
        "val_loss": val_loss,
    }, final_path)
    print(f"\nTraining complete! Best val loss: {best_val_loss:.4f}")
    print(f"Models saved to: {cfg['output_dir']}/")


if __name__ == "__main__":
    main()
