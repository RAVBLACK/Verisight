import io
import os
import sys

# Ensure api directory is on sys.path for local and serverless execution
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

from detector_onnx import analyze_image_onnx

app = FastAPI(
    title="Verisight API (Serverless)",
    description="Experimental AI-generated image detector powered by ONNX Runtime",
    version="0.2.0",
)

frontend_origin = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_origin,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@app.get("/")
def root():
    return {"message": "Verisight Serverless API is running"}


@app.get("/health")
def health():
    return {"status": "ok", "engine": "onnxruntime"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Upload a JPG, PNG, or WebP image.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image must be 10 MB or smaller.",
        )

    try:
        with Image.open(io.BytesIO(content)) as image:
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise HTTPException(
                    status_code=415,
                    detail="Unsupported image format.",
                )

            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="Image dimensions are too large.",
                )

            image.load()
            result = analyze_image_onnx(image.copy())

    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                f"The detector could not run: {str(exc)}"
            ),
        ) from exc

    return result
