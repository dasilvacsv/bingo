import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor
import keyboard

class RegionSelector:
    def __init__(self):
        self.start_pos = None
        self.current_pos = None
        self.is_selecting = False
        
        # Create transparent fullscreen window
        self.app = QApplication(sys.argv)
        self.window = FullscreenWindow()
        
    def get_region(self):
        self.window.show()
        self.app.exec_()
        return self.window.selected_region

class FullscreenWindow(QWidget):
    def __init__(self):
        super().__init__()
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
                self.selected_region = (x, y, width, height)
                print(f"Selected region: {self.selected_region}")
            self.close()

if __name__ == "__main__":
    selector = RegionSelector()
    region = selector.get_region()
    print(f"Final selected region: {region}")