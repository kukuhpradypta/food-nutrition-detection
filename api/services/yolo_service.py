"""
YOLO service - validates whether an image contains food.
Uses YOLOv8 pretrained on COCO dataset to detect food-related objects.
"""
from PIL import Image

# COCO classes that are considered food
FOOD_CLASSES = {
    "banana", "apple", "sandwich", "orange", "broccoli",
    "carrot", "hot dog", "pizza", "donut", "cake",
    "bowl", "cup", "fork", "knife", "spoon",
    # broader food containers
    "bottle", "wine glass", "dining table",
}

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.35


class YoloService:
    """Singleton service for YOLO food validation."""

    def __init__(self):
        self.model = None

    def load(self):
        """Load YOLOv8n model (auto-downloads on first run)."""
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            print("YOLO model loaded")
        except ImportError:
            print("WARNING: ultralytics not installed. YOLO validation disabled.")
            self.model = None

    def is_food(self, image: Image.Image) -> tuple[bool, list]:
        """
        Check if image contains food.
        Returns (is_food: bool, detected_labels: list)
        """
        if self.model is None:
            # If YOLO not available, skip validation and allow
            return True, []

        results = self.model(image, verbose=False)
        detected = []

        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = result.names[class_id].lower()

                if confidence >= CONFIDENCE_THRESHOLD:
                    detected.append({"label": label, "confidence": round(confidence, 2)})

        # Check if any detected object is food-related
        detected_labels = {d["label"] for d in detected}
        food_found = bool(detected_labels & FOOD_CLASSES)

        return food_found, detected


# Singleton instance
_yolo_service = YoloService()


def get_yolo_service() -> YoloService:
    return _yolo_service
