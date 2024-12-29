import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor
from mss import mss
from datetime import datetime
import os
import keyboard

class RegionSelector(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background:transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False
        self.selected_region = None
        
    def paintEvent(self, event):
        if self.is_selecting and self.start_pos and self.current_pos:
            painter = QPainter(self)
            painter.setPen(QColor(255, 0, 0))
            
            x = min(self.start_pos.x(), self.current_pos.x())
            y = min(self.start_pos.y(), self.current_pos.y())
            width = abs(self.start_pos.x() - self.current_pos.x())
            height = abs(self.start_pos.y() - self.current_pos.y())
            
            painter.drawRect(x, y, width, height)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.is_selecting = True
            
    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.current_pos = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            if self.start_pos and self.current_pos:
                x = min(self.start_pos.x(), self.current_pos.x())
                y = min(self.start_pos.y(), self.current_pos.y())
                width = abs(self.start_pos.x() - self.current_pos.x())
                height = abs(self.start_pos.y() - self.current_pos.y())
                self.selected_region = {"top": y, "left": x, "width": width, "height": height}
                self.callback(self.selected_region)
            self.close()

class ScreenshotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Region Screenshot Taker")
        self.setGeometry(100, 100, 300, 150)
        
        # Initialize screenshot capturer
        self.sct = mss()
        self.region = None
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create select region button
        self.select_button = QPushButton("Select Region")
        self.select_button.clicked.connect(self.start_region_selection)
        layout.addWidget(self.select_button)
        
        # Create status label
        self.status_label = QLabel("Select a region first")
        layout.addWidget(self.status_label)
        
        # Create counter label
        self.counter = 0
        self.counter_label = QLabel("Screenshots taken: 0")
        layout.addWidget(self.counter_label)
        
        # Keep window on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Listen for keyboard events
        keyboard.on_press(self.on_key_press)

    def start_region_selection(self):
        self.hide()  # Hide the main window during selection
        self.selector = RegionSelector(self.region_selected)
        self.selector.show()

    def region_selected(self, region):
        self.region = region
        self.status_label.setText(f"Press 'Space' to capture region: {region}")
        self.show()  # Show the main window again

    def on_key_press(self, event):
        if event.name == 'space' and self.region:
            self.take_screenshot()

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
            
            # Take screenshot of the specified region
            screenshot = self.sct.grab(self.region)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
            
            # Update counter
            self.counter += 1
            self.counter_label.setText(f"Screenshots taken: {self.counter}")
            self.status_label.setText(f"Screenshot saved as: {filename}")
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            self.status_label.setText(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()