import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer
from mss import mss
from datetime import datetime
import os

class ScreenshotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot Taker")
        self.setGeometry(100, 100, 300, 150)
        
        # Initialize screenshot capturer
        self.sct = mss()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create status label
        self.status_label = QLabel("Status: Stopped")
        layout.addWidget(self.status_label)
        
        # Create button
        self.toggle_button = QPushButton("Start Capturing")
        self.toggle_button.clicked.connect(self.toggle_capture)
        layout.addWidget(self.toggle_button)
        
        # Create counter label
        self.counter = 0
        self.counter_label = QLabel("Screenshots taken: 0")
        layout.addWidget(self.counter_label)
        
        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.take_screenshot)
        self.is_running = False

    def toggle_capture(self):
        if not self.is_running:
            self.is_running = True
            self.toggle_button.setText("Stop Capturing")
            self.status_label.setText("Status: Running")
            self.timer.start(2000)  # 2000 ms = 2 seconds
        else:
            self.is_running = False
            self.toggle_button.setText("Start Capturing")
            self.status_label.setText("Status: Stopped")
            self.timer.stop()

    def take_screenshot(self):
        try:
            # Create output folder
            output_folder = "screenshots"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(output_folder, filename)
            
            # Take screenshot of the entire screen
            screenshot = self.sct.shot(output=filepath)
            
            # Update counter
            self.counter += 1
            self.counter_label.setText(f"Screenshots taken: {self.counter}")
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            self.toggle_capture()  # Stop capturing on error

def main():
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()