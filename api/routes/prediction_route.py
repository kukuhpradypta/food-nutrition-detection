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
from api.services.yolo_service import get_yolo_service
from api.schemas.user_schema import ApiResponse


router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/", response_model=ApiResponse)
async def predict(file: UploadFile = File(...)):
    """
    Single image prediction via REST.

    1. Validates image contains food using YOLO
    2. If food detected, runs nutrition prediction model

    Upload a food image and get nutrition prediction (calories, fat, carbs, protein).
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Step 1: Validate with YOLO
        yolo_service = get_yolo_service()
        is_food, detected = yolo_service.is_food(image)

        if not is_food:
            return ApiResponse(
                status=422,
                message="Failed: object isn't food",
                data={"detected_objects": detected},
            )

        # Step 2: Run nutrition prediction
        model_service = get_model_service()
        result = model_service.predict(image)

        return ApiResponse(
            status=200,
            message="Prediction successful",
            data=result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.websocket("/ws")
async def websocket_predict(websocket: WebSocket):
    """
    Real-time prediction via WebSocket.

    Protocol:
    - Client connects to ws://server:8000/predict/ws
    - Client sends frame as base64 encoded JPEG/PNG string
    - Server responds with JSON nutrition prediction or error if not food
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

                # Step 1: Validate with YOLO
                yolo_service = get_yolo_service()
                is_food, detected = yolo_service.is_food(image)

                if not is_food:
                    await websocket.send_text(json.dumps({
                        "status": 422,
                        "message": "Failed: object isn't food",
                        "data": {"detected_objects": detected},
                    }))
                    continue

                # Step 2: Run nutrition prediction
                model_service = get_model_service()
                result = model_service.predict(image)
                elapsed_ms = (time.time() - start_time) * 1000
                result["processing_ms"] = round(elapsed_ms, 1)

                await websocket.send_text(json.dumps({
                    "status": 200,
                    "message": "Prediction successful",
                    "data": result,
                }))

            except Exception as e:
                await websocket.send_text(json.dumps({
                    "status": 500,
                    "message": f"Prediction failed: {str(e)}",
                    "data": None,
                }))

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
