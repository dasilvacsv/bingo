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
    
    # Define the region for the big number (using measured coordinates)
    top = int(height * 0.070)     # Measured exact position
    bottom = int(height * 0.187)   # Measured exact position
    left = int(width * 0.792)      # Measured exact position
    right = int(width * 0.856)     # Measured exact position
    
    # Print dimensions for debugging
    print(f"Image dimensions: {width}x{height}")
    print(f"ROI dimensions: {right-left}x{bottom-top}")
    print(f"ROI coordinates: ({left},{top}) to ({right},{bottom}")
    
    # Crop the image
    roi = img[top:bottom, left:right]
    
    # Save the ROI for debugging
    debug_folder = "debug"
    os.makedirs(debug_folder, exist_ok=True)
    cv2.imwrite(f"{debug_folder}/roi.png", roi)
    
    # Crop the image
    roi = img[top:bottom, left:right]
    
    # Add some padding to the coordinates
    pad = 10  # pixels of padding
    top = max(0, int(height * 0.070) - pad)
    bottom = min(height, int(height * 0.187) + pad)
    left = max(0, int(width * 0.792) - pad)
    right = min(width, int(width * 0.856) + pad)
    
    # Crop the image
    roi = img[top:bottom, left:right]
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Save the grayscale image for debugging
    cv2.imwrite(f"{debug_folder}/01_gray.png", gray)
    
    # Apply binary thresholding
    _, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(f"{debug_folder}/02_binary.png", thresh1)
    
    # Apply Otsu's thresholding
    _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(f"{debug_folder}/03_otsu.png", thresh2)
    
    # Create a debug folder
    debug_folder = "debug"
    os.makedirs(debug_folder, exist_ok=True)

    # Try both thresholded images with OCR
    custom_config = r'--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    
    number1 = pytesseract.image_to_string(thresh1, config=custom_config).strip()
    number2 = pytesseract.image_to_string(thresh2, config=custom_config).strip()
    
    print(f"Binary threshold OCR result: {number1}")
    print(f"Otsu threshold OCR result: {number2}")
    
    # Use the result that gave us digits
    number = number1 if number1.isdigit() else number2 if number2.isdigit() else ""
    
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