"""
Main application entry point for Face Recognition API
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import router
from config.settings import settings

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Face Recognition API built with Python, FastAPI, and face_recognition library.

    ## Features

    * **Face Detection** - Detect faces in images
    * **Face Recognition** - Recognize known faces in images
    * **Face Management** - Add and remove known faces
    * **Facial Landmarks** - Extract detailed facial features

    ## Endpoints

    * `/health` - Health check
    * `/recognize` - Recognize faces in an image
    * `/faces/add` - Add a known face
    * `/faces/{name}` - Remove a known face
    * `/faces` - List all known faces
    * `/detect` - Detect faces without recognition
    * `/landmarks` - Get facial landmarks
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.api_prefix, tags=["Face Recognition"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.api_prefix}/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
