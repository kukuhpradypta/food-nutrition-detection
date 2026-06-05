"""
FastAPI server with MVC structure for food nutrition prediction.

Endpoints:
    GET  /              → Status check
    GET  /health        → Model health check
    GET  /docs          → Scalar API docs
    POST /predict/      → Single image prediction
    WS   /predict/ws    → Real-time WebSocket prediction

Usage:
    uvicorn api.main:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

from api.database import Base
from api.models import User  # noqa: F401 - register models
from api.routes import prediction_router, user_router
from api.services.model_service import get_model_service

# ============ App Setup ============
app = FastAPI(
    title="Food Nutrition API",
    description="Real-time food nutrition prediction with MVC architecture",
    version="3.0.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Global Exception Handlers ============
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [f"{' -> '.join(str(l) for l in e['loc'])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"status": 422, "message": "Validasi gagal", "data": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": 500, "message": f"Server error: {str(exc)}", "data": None},
    )


# ============ Register Routes ============
app.include_router(prediction_router)
app.include_router(user_router)


# ============ Startup ============
@app.on_event("startup")
def on_startup():
    # Load ML model
    model_service = get_model_service()
    model_service.load()


# ============ Base Endpoints ============
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Food Nutrition API v3 - MVC + Scalar",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    model_service = get_model_service()
    return {
        "status": "healthy",
        "model_loaded": model_service.is_loaded,
        "device": str(model_service.device),
    }


# ============ Scalar API Docs at /docs ============
@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def scalar_docs():
    """Scalar API documentation UI."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Food Nutrition API - Docs</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
    </head>
    <body>
        <script
            id="api-reference"
            data-url="/openapi.json"
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
    </body>
    </html>
    """
