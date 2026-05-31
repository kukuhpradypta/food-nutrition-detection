"""
Test WebSocket client - simulates mobile camera sending frames.

Usage:
    1. Start server: uvicorn api.main:app --host 0.0.0.0 --port 8000
    2. Run this:     python api/test_websocket.py
"""
import asyncio
import base64
import json
import time
import websockets


async def test_realtime():
    uri = "ws://localhost:8000/predict/ws"

    async with websockets.connect(uri) as ws:
        print("Connected to WebSocket server")
        print("Simulating camera frames...\n")

        # Simulate sending 5 frames (like a camera would)
        test_images = [
            "image_resource/dish_1556572657.png",
            "image_resource/dish_1556573514.png",
            "image_resource/dish_1556575014.png",
            "image_resource/dish_1556575273.png",
            "image_resource/dish_1557853429.png",
        ]

        for i, img_path in enumerate(test_images):
            # Read and encode image (simulates camera capture)
            with open(img_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")

            # Send frame
            start = time.time()
            await ws.send(image_base64)

            # Receive prediction
            response = await ws.recv()
            result = json.loads(response)
            elapsed = (time.time() - start) * 1000

            print(f"Frame {i+1}: {result}")
            print(f"  Round-trip: {elapsed:.0f}ms | Server processing: {result.get('processing_ms', '?')}ms")
            print()

            # Simulate ~2 FPS camera
            await asyncio.sleep(0.5)

        print("Done! WebSocket real-time prediction works.")


if __name__ == "__main__":
    asyncio.run(test_realtime())
