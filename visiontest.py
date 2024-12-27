import cv2
import numpy as np

def click_and_crop(event, x, y, flags, param):
    global points, image_copy
    
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        # Draw the point
        cv2.circle(image_copy, (x, y), 3, (0, 255, 0), -1)
        
        if len(points) == 2:
            # Draw rectangle
            cv2.rectangle(image_copy, points[0], points[1], (0, 255, 0), 2)
            # Calculate and display coordinates and dimensions
            x1, y1 = points[0]
            x2, y2 = points[1]
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            print(f"\nSelected Region:")
            print(f"Top-left: ({min(x1, x2)}, {min(y1, y2)})")
            print(f"Bottom-right: ({max(x1, x2)}, {max(y1, y2)})")
            print(f"Width: {width}, Height: {height}")
            print(f"\nFor the script:")
            print(f"left = int(width * {min(x1, x2)/image.shape[1]:.3f})")
            print(f"right = int(width * {max(x1, x2)/image.shape[1]:.3f})")
            print(f"top = int(height * {min(y1, y2)/image.shape[0]:.3f})")
            print(f"bottom = int(height * {max(y1, y2)/image.shape[0]:.3f})")

# Read the image
image = cv2.imread('bingo_test.png')  # Replace with your image name
if image is None:
    print("Error: Could not read image")
    exit()

image_copy = image.copy()
points = []

# Create window and set mouse callback
cv2.namedWindow('Image')
cv2.setMouseCallback('Image', click_and_crop)

print("Click two points to define the region (top-left and bottom-right corners)")
print("Press 'r' to reset or 'q' to quit")

while True:
    cv2.imshow('Image', image_copy)
    key = cv2.waitKey(1) & 0xFF
    
    # Reset if 'r' is pressed
    if key == ord('r'):
        image_copy = image.copy()
        points = []
        print("\nPoints reset. Click again.")
    
    # Break if 'q' is pressed
    elif key == ord('q'):
        break

cv2.destroyAllWindows()