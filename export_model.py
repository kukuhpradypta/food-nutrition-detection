"""
Export trained model to ONNX format for mobile deployment.
ONNX can be used with:
  - Android: ONNX Runtime Mobile / TensorFlow Lite (via conversion)
  - iOS: Core ML (via coremltools conversion) / ONNX Runtime

Usage:
    python export_model.py
"""
import os
import torch
import torch.nn as nn
import torch.onnx
from model import create_model

CHECKPOINT_PATH = "checkpoints/best_model.pth"
EXPORT_DIR = "exported_models"
IMAGE_SIZE = 224


class DenormalizedModel(nn.Module):
    """
    Wraps the trained model so its output is denormalized back to real units
    (calories, fat_g, carb_g, protein_g) and clamped to >= 0.
    This makes the exported ONNX/TorchScript model directly usable on mobile
    without needing the mean/std on the client side.
    """

    def __init__(self, base_model, target_mean, target_std):
        super().__init__()
        self.base_model = base_model
        self.register_buffer("target_mean", target_mean)
        self.register_buffer("target_std", target_std)

    def forward(self, x):
        out = self.base_model(x)
        out = out * self.target_std + self.target_mean
        return torch.clamp(out, min=0.0)


def _load_wrapped_model():
    """Load checkpoint and wrap with denormalization."""
    model = create_model(pretrained=False)
    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    mean = checkpoint.get("target_mean")
    std = checkpoint.get("target_std")
    if mean is None or std is None:
        # Fallback: identity (no normalization)
        mean = torch.zeros(4)
        std = torch.ones(4)

    wrapped = DenormalizedModel(model, mean.float(), std.float())
    wrapped.eval()
    return wrapped


def export_onnx():
    """Export model to ONNX format."""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    model = _load_wrapped_model()

    # Dummy input
    dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)

    # Export to ONNX
    onnx_path = os.path.join(EXPORT_DIR, "food_nutrition_model.onnx")
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=13,
        do_constant_folding=True,
        input_names=["image"],
        output_names=["nutrition"],
        dynamic_axes={
            "image": {0: "batch_size"},
            "nutrition": {0: "batch_size"},
        },
    )
    print(f"ONNX model saved to: {onnx_path}")
    print(f"Model size: {os.path.getsize(onnx_path) / 1024 / 1024:.2f} MB")


def export_torchscript():
    """Export model to TorchScript for PyTorch Mobile."""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    model = _load_wrapped_model()

    # Trace model
    dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    traced_model = torch.jit.trace(model, dummy_input)

    # Optimize for mobile
    from torch.utils.mobile_optimizer import optimize_for_mobile
    optimized_model = optimize_for_mobile(traced_model)

    # Save
    ts_path = os.path.join(EXPORT_DIR, "food_nutrition_model.ptl")
    optimized_model._save_for_lite_interpreter(ts_path)
    print(f"TorchScript Lite model saved to: {ts_path}")
    print(f"Model size: {os.path.getsize(ts_path) / 1024 / 1024:.2f} MB")


def main():
    print("=" * 50)
    print("Exporting model for mobile deployment")
    print("=" * 50)

    print("\n--- ONNX Export ---")
    export_onnx()

    print("\n--- TorchScript Mobile Export ---")
    try:
        export_torchscript()
    except Exception as e:
        print(f"TorchScript export failed (optional): {e}")
        print("ONNX export is sufficient for mobile deployment.")

    print("\n" + "=" * 50)
    print("Export complete!")
    print("\nOutput format: [calories, fat, carb, protein]")
    print("Input: RGB image normalized with ImageNet mean/std, size 224x224")
    print("\nFor mobile integration:")
    print("  Android -> Use ONNX Runtime Mobile")
    print("  iOS     -> Convert ONNX to CoreML with coremltools")
    print("  Flutter -> Use tflite_flutter (convert ONNX to TFLite)")


if __name__ == "__main__":
    main()
