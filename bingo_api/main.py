from fastapi import FastAPI, File, UploadFile, Request
import os
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import pytesseract
import io
from PIL import Image

app = FastAPI(title="Bingo Number Detector")

# Templates configuration
templates = Jinja2Templates(directory="templates")

def format_number(number: str) -> str:
    """Format a number with its BINGO letter prefix."""
    try:
        num = int(number)
        if 1 <= num <= 15:
            return f"B{num}"
        elif 16 <= num <= 30:
            return f"I{num}"
        elif 31 <= num <= 45:
            return f"N{num}"
        elif 46 <= num <= 60:
            return f"G{num}"
        elif 61 <= num <= 75:
            return f"O{num}"
        else:
            return number
    except ValueError:
        return number

def process_image(image_bytes):
    """Process image bytes to extract the bingo number."""
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not process image")
    
    # Get dimensions
    height, width = img.shape[:2]
    
    # Define the region for the big number with padding
    pad = 5
    top = max(0, int(height * 0.070) - pad)
    bottom = min(height, int(height * 0.187) + pad)
    left = max(0, int(width * 0.792) - pad)
    right = min(width, int(width * 0.856) + pad)
    
    # Crop the image
    roi = img[top:bottom, left:right]
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )
    
    # OCR Configuration
    custom_config = r'--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    
    # Try OCR on both images
    number_gray = pytesseract.image_to_string(gray, config=custom_config).strip()
    number_binary = pytesseract.image_to_string(binary, config=custom_config).strip()
    
    # Use the result that gives us digits
    number = ''
    for result in [number_gray, number_binary]:
        cleaned = ''.join(filter(str.isdigit, result))
        if cleaned:
            number = cleaned
            break

    # Format the number with BINGO letter and return
    return format_number(number) if number else ""
    
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "upload.html", 
        {"request": request}
    )

@app.get("/calibrate", response_class=HTMLResponse)
async def calibrate_page(request: Request):
    return templates.TemplateResponse(
        "calibrate.html",
        {"request": request}
    )

@app.post("/api/upload-calibration")
async def upload_calibration_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # Store the image temporarily or in memory
        # Return a success response with the image data
        return {
            "success": True,
            "image": contents.decode('latin1')  # Encode binary data for frontend
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/detect")
async def detect_number(file: UploadFile = File(...)):
    try:
        # Read image file
        contents = await file.read()
        
        # Process the image
        number = process_image(contents)
        
        if not number:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not detect any number"}
            )
        
        return {"number": number}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        number = process_image(contents)
        
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "number": number if number else "No number detected"
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)