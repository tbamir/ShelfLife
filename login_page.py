import sys
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from user import User  # Import User model
from storage import register_user, login_user  # Import storage methods


class LoginPage(QWidget):
    def __init__(self, parent=None, login_callback=None):
        super().__init__(parent)
        self.login_callback = login_callback
        self.count = 0  # Track login attempts
        self.locked_until = None  # Track when the user can try logging in again
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login Page")
        self.setStyleSheet("background-color: #1d322b;")
        self.resize(600, 700)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Form Layout
        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setContentsMargins(10, 20, 10, 20)
        form_layout.setSpacing(15)

        username_label = QLabel("Username")
        username_label.setStyleSheet("background-color: #c87f4a; color: white; padding: 5px; border: 2px ridge #855330;")
        username_label.setFont(QFont("BahnSchrift SemiBold", 16))

        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Enter your username")
        self.username_entry.setFont(QFont("BahnSchrift SemiBold", 16))
        self.username_entry.setStyleSheet("padding: 5px; color: white; background-color: #2f3d36; border: 2px solid #c87f4a;")

        form_layout.addRow(username_label, self.username_entry)

        password_label = QLabel("Password")
        password_label.setStyleSheet("background-color: #c87f4a; color: white; padding: 5px; border: 2px ridge #855330;")
        password_label.setFont(QFont("BahnSchrift SemiBold", 16))

        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter your password")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFont(QFont("BahnSchrift", 16))
        self.password_entry.setStyleSheet("padding: 5px; color: white; background-color: #2f3d36; border: 2px solid #c87f4a;")

        form_layout.addRow(password_label, self.password_entry)
        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)

        login_button = QPushButton("Login")
        login_button.setFont(QFont("BahnSchrift SemiBold", 18))
        login_button.setFixedSize(250, 50)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #c87f4a; 
                color: white; 
                padding: 10px; 
                border-radius: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a9613a;
            }
        """)
        login_button.clicked.connect(self.login)

        register_button = QPushButton("Register")
        register_button.setFont(QFont("BahnSchrift SemiBold", 18))
        register_button.setFixedSize(250, 50)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #c87f4a; 
                color: white; 
                padding: 10px; 
                border-radius: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a9613a;
            }
        """)
        register_button.clicked.connect(self.register)

        button_layout.addWidget(login_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(register_button, alignment=Qt.AlignCenter)

        main_layout.addLayout(button_layout)

        # Error Label
        self.error_label = QLabel("")
        self.error_label.setFont(QFont("BahnSchrift", 12, QFont.Bold))
        self.error_label.setStyleSheet("color: orange;")
        self.error_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.error_label)

        self.setLayout(main_layout)

    def login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()

        if login_user(username, password):
            self.count = 0  # Reset count on success
            user = User(username)
            if self.login_callback:
                self.login_callback(user)
        else:
            self.count += 1
            self.error_label.setText("Invalid username or password.")
            
    def register(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()

        if not username or not password:
            self.error_label.setText("Username and password cannot be empty")
            return

        if register_user(username, password):
            self.error_label.setText("Registration successful! Please log in.")
        else:
            self.error_label.setText("Username already exists. Choose a different username.")