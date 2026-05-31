"""
Prediction routes - API endpoint definitions.
"""
import io
import base64
import json
import time

from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from PIL import Image
from pydantic import BaseModel

from api.services.model_service import get_model_service


class NutritionResponse(BaseModel):
    calories: float
    fat_g: float
    carb_g: float
    protein_g: float


router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/", response_model=NutritionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Single image prediction via REST.

    Upload a food image and get nutrition prediction (calories, fat, carbs, protein).
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        model_service = get_model_service()
        result = model_service.predict(image)
        return NutritionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.websocket("/ws")
async def websocket_predict(websocket: WebSocket):
    """
    Real-time prediction via WebSocket.

    Protocol:
    - Client connects to ws://server:8000/predict/ws
    - Client sends frame as base64 encoded JPEG/PNG string
    - Server responds with JSON nutrition prediction
    """
    await websocket.accept()
    print("WebSocket client connected")

    try:
        while True:
            data = await websocket.receive_text()
            start_time = time.time()

            try:
                image_bytes = base64.b64decode(data)
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                model_service = get_model_service()
                result = model_service.predict(image)
                elapsed_ms = (time.time() - start_time) * 1000
                result["processing_ms"] = round(elapsed_ms, 1)
                await websocket.send_text(json.dumps(result))
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                await websocket.send_text(error_msg)

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
