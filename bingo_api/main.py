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
    
    # Define the region for the big number (adjusted for the circular display)
    top = int(height * 0.05)
    bottom = int(height * 0.20)  # Reduced to focus on the circle
    left = int(width * 0.15)     # Moved left to catch the full circle
    right = int(width * 0.35)    # Adjusted width accordingly
    
    # Crop the image
    roi = img[top:bottom, left:right]
    
    # Convert to HSV to handle the yellow background better
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Create a mask for the dark text
    lower = np.array([0, 0, 0])
    upper = np.array([180, 255, 100])
    mask = cv2.inRange(hsv, lower, upper)
    
    # Apply some morphological operations to clean up the text
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)
    
    # Save debug images
    debug_folder = "debug"
    os.makedirs(debug_folder, exist_ok=True)
    cv2.imwrite(f"{debug_folder}/roi.png", roi)
    cv2.imwrite(f"{debug_folder}/mask.png", mask)
    
    # OCR with adjusted settings
    number = pytesseract.image_to_string(mask, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    
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