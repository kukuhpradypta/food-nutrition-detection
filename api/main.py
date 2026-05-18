"""
FastAPI server with WebSocket for real-time food nutrition prediction.

Endpoints:
    GET  /              → Status check
    GET  /health        → Model health check
    POST /predict       → Single image prediction
    WS   /ws/predict    → Real-time WebSocket prediction (for camera stream)

Usage:
    uvicorn api.main:app --host 0.0.0.0 --port 8000
"""
import io
import sys
import os
import base64
import json
import asyncio
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_transform import get_val_transforms
from model import create_model

# ============ Config ============
CHECKPOINT_PATH = "checkpoints/best_model.pth"
IMAGE_SIZE = 224

# ============ App Setup ============
app = FastAPI(
    title="Food Nutrition API",
    description="Real-time food nutrition prediction via WebSocket",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Response Model ============
class NutritionResponse(BaseModel):
    calories: float
    fat_g: float
    carb_g: float
    protein_g: float


# ============ Load Model ============
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
transform = None


@app.on_event("startup")
def load_model():
    global model, transform
    model = create_model(pretrained=False)
    checkpoint = torch.load(CHECKPOINT_PATH, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    transform = get_val_transforms(IMAGE_SIZE)
    print(f"Model loaded on {device}")


def predict_image(image: Image.Image) -> dict:
    """Core prediction logic, shared by REST and WebSocket."""
    input_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)
    calories, fat, carb, protein = output[0].cpu().numpy()
    return {
        "calories": round(float(calories), 1),
        "fat_g": round(float(fat), 2),
        "carb_g": round(float(carb), 2),
        "protein_g": round(float(protein), 2),
    }


# ============ REST Endpoints ============
@app.get("/")
def root():
    return {"status": "ok", "message": "Food Nutrition API v2 - WebSocket enabled"}


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None, "device": str(device)}


@app.post("/predict", response_model=NutritionResponse)
async def predict(file: UploadFile = File(...)):
    """Single image prediction via REST."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        result = predict_image(image)
        return NutritionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ============ WebSocket Endpoint ============
@app.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    """
    Real-time prediction via WebSocket.

    Protocol:
    - Client connects to ws://server:8000/ws/predict
    - Client sends frame as base64 encoded JPEG/PNG string
    - Server responds with JSON: {"calories": ..., "fat_g": ..., "carb_g": ..., "protein_g": ..., "fps": ...}

    Client can send frames as fast as it wants.
    Server will process and respond to each frame.
    """
    await websocket.accept()
    print("WebSocket client connected")

    try:
        while True:
            # Receive frame from client (base64 encoded image)
            data = await websocket.receive_text()

            start_time = time.time()

            try:
                # Decode base64 image
                image_bytes = base64.b64decode(data)
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

                # Predict
                result = predict_image(image)

                # Add processing time info
                elapsed_ms = (time.time() - start_time) * 1000
                result["processing_ms"] = round(elapsed_ms, 1)

                # Send result back
                await websocket.send_text(json.dumps(result))

            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                await websocket.send_text(error_msg)

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
