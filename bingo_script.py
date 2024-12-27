import cv2
import numpy as np
import pytesseract
from PIL import Image

def detect_number(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Get dimensions
    height, width = img.shape[:2]
    
    # Define the region of interest (ROI) for the big number
    # These values are approximate based on the image - you might need to adjust
    top = int(height * 0.05)  # Top 5% of image
    bottom = int(height * 0.3)  # 30% down
    left = int(width * 0.2)     # Left 20%
    right = int(width * 0.5)    # Right 50%
    
    # Crop the image to the ROI
    roi = img[top:bottom, left:right]
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Threshold the image
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # OCR to get the number
    number = pytesseract.image_to_string(thresh, config='--psm 7 digits')
    
    # Clean the result
    number = ''.join(filter(str.isdigit, number))
    
    # Save debug images
    cv2.imwrite('debug_roi.png', roi)
    cv2.imwrite('debug_thresh.png', thresh)
    
    return number

def main():
    image_path = 'bingo_test.png'  # Save your image with this name
    try:
        number = detect_number(image_path)
        print(f"Detected number: {number}")
        
        # If you want to send to webhook:
        # webhook_url = "YOUR_WEBHOOK_URL"
        # send_webhook(number, webhook_url)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()