import sys
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QMainWindow, QStackedWidget, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt, QRect, QTimer
from login_page import LoginPage
from book_search_page import BookSearchPage
from collection_page import CollectionPage
from wishlist_page import WishlistPage

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Frameless and translucent splash screen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Resize and center the splash screen
        self.resize(400, 400)
        self.center()

        # Layout for the splash screen
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Animated GIF for splash
        self.animation_label = QLabel(self)
        movie = QMovie("images/splash_screen.gif")
        movie.setScaledSize(QRect(0, 0, 300, 200).size())  # Scale GIF to fit smaller area
        self.animation_label.setMovie(movie)
        movie.start()

        # Title Label
        self.title_label = QLabel("Welcome to ShelfLife Book Manager", self)
        self.title_label.setStyleSheet("""
            font-size: 20px;
            color: white;
            font-weight: bold;
        """)

        # Add widgets to layout
        layout.addWidget(self.animation_label)
        layout.addWidget(self.title_label)

    def center(self):
        # Center the splash screen on the user's screen
        screen = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        x = (screen.width() - widget_geometry.width()) // 2
        y = (screen.height() - widget_geometry.height()) // 2


class AppController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shelf Life Book Manager")
        self.setGeometry(100, 100, 800, 900)  # Increased size for better UI experience
        self.current_user = None

        # Apply custom styling
        self.apply_styles()

        # Logo section with customized background
        self.logo_container = QWidget()
        self.logo_container.setFixedHeight(150)
        self.logo_container.setStyleSheet("background-color: #1d322b;")
        self.logo_layout = QHBoxLayout(self.logo_container)
        self.logo_layout.setContentsMargins(10, 10, 10, 10)

        # Add logo to the logo section
        self.logo_label = QLabel()
        self.set_logo("images/Shelf_Life_logo_focus.png")  # Ensure you have a `logo.png` in the working directory
        self.logo_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.logo_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)

        # Central widget
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self.logo_container)

        self.stacked_widget = QStackedWidget()
        central_layout.addWidget(self.stacked_widget)

        # Set central widget with logo and stacked widgets
        self.setCentralWidget(central_widget)

        # Start with the login page
        self.show_login_page()

    def apply_styles(self):
        # Apply custom styles to the application.
        self.setStyleSheet("""
            QMainWindow {
                background-color: #c87f4a;  /* Soft neutral background for the main window */
            }
            QLabel {
                font-family: "Arial";
                font-size: 16px;
                color: #ccc;  /* Dark text color for readability */
            }
            QPushButton {
                background-color: #c87f4a;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-family: "Arial";
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #a9613a;
            }
            QPushButton:pressed {
                background-color: #c87f4a;
            }
            QStackedWidget {
                background-color: #1d322b;
                border: 1px solid #c87f4a;
                border-radius: 10px;
                padding: 10px;
            }
            QWidget#logo_container {
                border-bottom: 2px solid #c87f4a;  /* Separator line for logo section */
            }
        """)

    def set_logo(self, logo_path):
        # Set the application logo.
        try:
            pixmap = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error loading logo: {e}")

    def show_login_page(self):
        # Display the login page.
        login_page = LoginPage(self, self.on_login_success)
        self.stacked_widget.addWidget(login_page)
        self.stacked_widget.setCurrentWidget(login_page)

    def on_login_success(self, user):
        # Handle login success and move to the book search page.
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Login Success", f"Welcome, {user.username}!")
        self.current_user = user
        self.show_book_search_page()

    def show_book_search_page(self):
        # Display the book search page.
        book_search_page = BookSearchPage(self.current_user, self.show_collection_page, self.show_wishlist_page, self.logout)
        self.stacked_widget.addWidget(book_search_page)
        self.stacked_widget.setCurrentWidget(book_search_page)

    def show_collection_page(self):
        # Display the user's book collection page.
        collection_page = CollectionPage(self.current_user, self.show_book_search_page, self.logout)
        self.stacked_widget.addWidget(collection_page)
        self.stacked_widget.setCurrentWidget(collection_page)

    def show_wishlist_page(self):
        # Display the user's wishlist page
        wishlist_page = WishlistPage(self.current_user, self.show_book_search_page, self.logout)
        self.stacked_widget.addWidget(wishlist_page)
        self.stacked_widget.setCurrentWidget(wishlist_page)

    def logout(self):
        # Handle user logout and return to the login page.
        from PyQt5.QtWidgets import QMessageBox
        self.current_user = None
        QMessageBox.information(self, "Logout", "You have been logged out successfully.")
        self.show_login_page()

def main():
    # Main entry point for the application.
    app = QApplication(sys.argv)

    # Show splash screen
    splash = SplashScreen()
    splash.show()

    controller = AppController()

    # Close splash and show main window after 3 seconds
    QTimer.singleShot(3000, splash.close)
    QTimer.singleShot(3000, controller.show)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()