import json
import cv2
import numpy as np
from typing import Dict, Optional

class BingoCalibrator:
    def __init__(self, calibration_file: str = "calibration.json"):
        self.calibration_file = calibration_file
        
    def load_calibration(self) -> Dict[str, float]:
        """Load calibration data from file"""
        try:
            with open(self.calibration_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "top": 0.070,
                "bottom": 0.187,
                "left": 0.792,
                "right": 0.856
            }

    def save_calibration(self, data: Dict[str, float]) -> None:
        """Save calibration data to file"""
        with open(self.calibration_file, 'w') as f:
            json.dump(data, f)

    def process_image_calibrated(self, image_bytes: bytes) -> Optional[Dict[str, int]]:
        """Process image using calibrated coordinates"""
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None
        
        # Get dimensions
        height, width = img.shape[:2]
        
        # Load calibration
        calibration = self.load_calibration()
        
        # Calculate regions based on calibration
        pad = 5
        top = max(0, int(height * calibration["top"]) - pad)
        bottom = min(height, int(height * calibration["bottom"]) + pad)
        left = max(0, int(width * calibration["left"]) - pad)
        right = min(width, int(width * calibration["right"]) + pad)
        
        return {
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right
        }