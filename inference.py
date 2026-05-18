"""
Inference script: predict nutrition from a single food image.
Simulates what the mobile app will do.

Usage:
    python inference.py --image path/to/food_image.png
"""
import argparse
import torch
from PIL import Image
from data_transform import get_val_transforms
from model import create_model

CHECKPOINT_PATH = "checkpoints/best_model.pth"
IMAGE_SIZE = 224


def predict(image_path, checkpoint_path=CHECKPOINT_PATH):
    """Predict nutrition values from a food image."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model
    model = create_model(pretrained=False)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    # Load and preprocess image
    transform = get_val_transforms(IMAGE_SIZE)
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        output = model(input_tensor)

    # Parse results
    calories, fat, carb, protein = output[0].cpu().numpy()

    return {
        "calories": round(float(calories), 1),
        "fat_g": round(float(fat), 2),
        "carb_g": round(float(carb), 2),
        "protein_g": round(float(protein), 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Predict food nutrition from image")
    parser.add_argument("--image", type=str, required=True, help="Path to food image")
    parser.add_argument("--checkpoint", type=str, default=CHECKPOINT_PATH)
    args = parser.parse_args()

    result = predict(args.image, args.checkpoint)

    print("\n" + "=" * 40)
    print("  Food Nutrition Prediction")
    print("=" * 40)
    print(f"  Calories : {result['calories']} kcal")
    print(f"  Fat      : {result['fat_g']} g")
    print(f"  Carbs    : {result['carb_g']} g")
    print(f"  Protein  : {result['protein_g']} g")
    print("=" * 40)


if __name__ == "__main__":
    main()
