import sys
import cv2
from pyzbar.pyzbar import decode
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

class Scanner:
    @staticmethod
    def scan():
        scan_dialog = BarcodeScannerDialog()
        result = scan_dialog.exec_()

        if result == QDialog.Accepted:
            return scan_dialog.scanned_isbn
        return None

class BarcodeScannerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Barcode Scanner")
        self.setGeometry(100, 100, 640, 480)
        
        # Set background color
        self.setStyleSheet("background-color: #1d322b;")

        layout = QVBoxLayout()

        self.camera_label = QLabel("Scanning for Barcode...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
        """)
        layout.addWidget(self.camera_label)

        self.status_label = QLabel("Position barcode in camera view")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #c87f4a;
            }
        """)
        layout.addWidget(self.status_label)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #c87f4a;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #a66a40;
            }
            QPushButton:pressed {
                background-color: #8a5c3c;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.scanned_isbn = None
        self.capture = None

        self.init_camera()

    def init_camera(self):
        try:
            self.capture = cv2.VideoCapture(0)

            if not self.capture.isOpened():
                raise Exception("Could not open camera")

            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.scan_frame)
            self.timer.start(100)

        except Exception as e:
            self.handle_camera_error(str(e))

    def scan_frame(self):
        if not self.capture:
            return

        ret, frame = self.capture.read()

        if not ret:
            self.status_label.setText("Failed to capture frame")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        barcodes = decode(rgb_frame)

        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')

                if self.validate_isbn(barcode_data):
                    self.scanned_isbn = barcode_data
                    self.status_label.setText(f"Scanned ISBN: {barcode_data}")
                    self.accept()
                    return

        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.camera_label.setPixmap(pixmap.scaled(
            self.camera_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))

    def validate_isbn(self, isbn):
        isbn = isbn.replace('-', '').replace(' ', '')

        return (len(isbn) == 10 or len(isbn) == 13) and isbn.isdigit()

    def handle_camera_error(self, error_msg):
        QMessageBox.critical(
            self, 
            "Camera Error", 
            f"Could not initialize camera: {error_msg}\n\n"
            "Please ensure:\n"
            "1. Camera is connected\n"
            "2. No other application is using the camera\n"
            "3. Camera drivers are installed"
        )
        self.reject()

    def closeEvent(self, event):
        if self.capture:
            self.capture.release()
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()