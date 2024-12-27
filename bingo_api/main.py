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
    """Process image bytes to extract the bingo number."""
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not process image")
    
    # Get dimensions
    height, width = img.shape[:2]
    
    # Create debug folder once
    debug_folder = "debug"
    os.makedirs(debug_folder, exist_ok=True)
    
    # Define the region for the big number with padding
    pad = 5  # pixels of padding
    top = max(0, int(height * 0.070) - pad)
    bottom = min(height, int(height * 0.187) + pad)
    left = max(0, int(width * 0.792) - pad)
    right = min(width, int(width * 0.856) + pad)
    
    # Crop the image
    roi = img[top:bottom, left:right]
    cv2.imwrite(f"{debug_folder}/01_roi.png", roi)
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"{debug_folder}/02_gray.png", gray)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,  # Block size
        2    # C constant
    )
    cv2.imwrite(f"{debug_folder}/03_binary.png", binary)
    
    # Apply morphological operations to clean up the image
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    cv2.imwrite(f"{debug_folder}/04_morph.png", binary)
    
    # OCR Configuration for large, clear digits
    custom_config = r'--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    
    # Try OCR on both the original grayscale and the binary image
    number_gray = pytesseract.image_to_string(gray, config=custom_config).strip()
    number_binary = pytesseract.image_to_string(binary, config=custom_config).strip()
    
    print(f"Grayscale OCR result: {number_gray}")
    print(f"Binary OCR result: {number_binary}")
    
    # Use the result that gives us digits
    number = ''
    for result in [number_gray, number_binary]:
        cleaned = ''.join(filter(str.isdigit, result))
        if cleaned:
            number = cleaned
            break
    
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