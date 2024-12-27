import cv2
import numpy as np
import pytesseract
import os

def detect_number(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    if img is None:
        raise Exception("Could not read image")
    
    # Get dimensions
    height, width = img.shape[:2]
    
    # Define the region for the big number (approximately where the 61 is)
    top = int(height * 0.05)
    bottom = int(height * 0.25)
    left = int(width * 0.25)
    right = int(width * 0.45)
    
    # Crop the image
    roi = img[top:bottom, left:right]
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Threshold
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Save debug images in /app/debug
    cv2.imwrite('/app/debug/roi.png', roi)
    cv2.imwrite('/app/debug/thresh.png', thresh)
    
    # OCR
    number = pytesseract.image_to_string(thresh, config='--psm 7 digits')
    
    # Clean the result
    number = ''.join(filter(str.isdigit, number))
    
    return number

def main():
    # Create debug directory
    os.makedirs('/app/debug', exist_ok=True)
    
    image_path = '/app/test.png'
    try:
        number = detect_number(image_path)
        print(f"Detected number: {number}")
        print("Debug images saved in /app/debug/")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()