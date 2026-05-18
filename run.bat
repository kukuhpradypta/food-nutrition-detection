@echo off
echo ============================================
echo   Food Nutrition Model - Full Pipeline
echo ============================================
echo.

:: Step 1: Install dependencies
echo [Step 1/5] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

:: Step 2: Prepare data
echo [Step 2/5] Preparing data (split train/val)...
python prepare_data.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to prepare data
    pause
    exit /b 1
)
echo.

:: Step 3: Train model
echo [Step 3/5] Training model...
python data_training.py
if %errorlevel% neq 0 (
    echo ERROR: Training failed
    pause
    exit /b 1
)
echo.

:: Step 4: Export model
echo [Step 4/5] Exporting model to ONNX...
python export_model.py
if %errorlevel% neq 0 (
    echo ERROR: Export failed
    pause
    exit /b 1
)
echo.

:: Step 5: Start API server
echo [Step 5/5] Starting API server...
echo Server will run at http://localhost:8000
echo WebSocket at ws://localhost:8000/ws/predict
echo Press Ctrl+C to stop
echo.
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

pause
