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

def process_image(image_bytes):
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not process image")
    
    # Get dimensions
    height, width = img.shape[:2]
    
    # Define the region for the big number (adjusted specifically for the circular display)
    top = int(height * 0.02)     # Start higher up
    bottom = int(height * 0.15)   # Just enough to capture the circle
    left = int(width * 0.05)      # Include the full left side of circle
    right = int(width * 0.25)     # And the right side
    
    # Print dimensions for debugging
    print(f"Image dimensions: {width}x{height}")
    print(f"ROI dimensions: {right-left}x{bottom-top}")
    
    # Crop the image
    roi = img[top:bottom, left:right]
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Use adaptive thresholding to handle the varying background
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )
    
    # Clean up noise
    kernel = np.ones((2,2), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Save additional debug image
    cv2.imwrite('debug/gray.png', gray)
    cv2.imwrite('debug/thresh.png', thresh)
    
    # Save debug images
    debug_folder = "debug"
    os.makedirs(debug_folder, exist_ok=True)
    cv2.imwrite(f"{debug_folder}/roi.png", roi)
    cv2.imwrite(f"{debug_folder}/mask.png", mask)
    
    # OCR with improved settings for large digits
    custom_config = r'--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    number = pytesseract.image_to_string(mask, config=custom_config)
    print(f"Raw OCR output: {number}")
    
    # Clean the result
    number = ''.join(filter(str.isdigit, number))
    
    return number

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "upload.html", 
        {"request": request}
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