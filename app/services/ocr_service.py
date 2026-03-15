import io
import requests
import numpy as np
from PIL import Image
import easyocr
from fastapi import UploadFile
import os
from dotenv import load_dotenv

load_dotenv()
# -------------------------
# CONFIG
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
if not ROBOFLOW_API_KEY:
    raise ValueError("ROBOFLOW_API_KEY environment variable not set")
MODEL_ENDPOINT = "book-spine-detection-2cci9/1"
OCR_LANGS = ['en']

# Initialize EasyOCR
reader = easyocr.Reader(OCR_LANGS, gpu=False)  # set gpu=False if no GPU

async def extract_text_from_image(image: UploadFile):
    """
    Receives an UploadFile from FastAPI, detects book spines using Roboflow,
    then runs OCR on each detected spine and returns a list of titles.
    """
    # Read image bytes from UploadFile
    image_bytes = await image.read()
    
    # Send to Roboflow API
    response = requests.post(
        f"https://serverless.roboflow.com/{MODEL_ENDPOINT}?api_key={ROBOFLOW_API_KEY}",
        files={"file": io.BytesIO(image_bytes)}
    )
    result = response.json()
    
    # Open original image for cropping
    orig_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    orig_cv = np.array(orig_image)
    
    titles = []
    for pred in result.get("predictions", []):
        # Roboflow returns center coordinates
        x = int(pred["x"])
        y = int(pred["y"])
        w = int(pred["width"])
        h = int(pred["height"])
        
        # Convert to bounding box coordinates
        left = max(0, x - w // 2)
        top = max(0, y - h // 2)
        right = min(orig_cv.shape[1], x + w // 2)
        bottom = min(orig_cv.shape[0], y + h // 2)
        
        spine_crop = orig_cv[top:bottom, left:right]
        
        # OCR on the spine
        ocr_result = reader.readtext(spine_crop)
        spine_title = " ".join([text for bbox, text, conf in ocr_result if conf > 0.3])
        
        if spine_title.strip():
            titles.append(spine_title.strip())
    
    return titles