from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QGridLayout, QApplication, QPushButton, QLabel, QHBoxLayout, QScrollArea, QFrame,
    QComboBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from storage import load_collection, save_collection


class BookCard(QFrame):
    def __init__(self, book, image_path, remove_callback, status_change_callback):
        super().__init__()

        # Card design and hover effect
        self.setStyleSheet("""
            BookCard {
                background-color: #EAD2A8;
                border-radius: 10px;
                border: 3px solid #c87f4a;
                padding: 10px;
            }
        """)

        # Enable hover effects
        self.setProperty("hover", True)

        # Main layout for the book card
        layout = QVBoxLayout()

        # Cover Image
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 225)
        self.image_label.setScaledContents(True)
        if image_path:
            pixmap = QPixmap(image_path).scaled(
                150, 225,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
        else:
            # Placeholder image
            pixmap = QPixmap(150, 225)
            pixmap.fill(Qt.lightGray)
            self.image_label.setPixmap(pixmap)

        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Book Title
        self.title_label = QLabel(book.title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: black;")  # Set text color to black
        layout.addWidget(self.title_label)

        # Author
        self.author_label = QLabel(book.author)
        self.author_label.setFont(QFont("Arial", 10))
        self.author_label.setAlignment(Qt.AlignCenter)
        self.author_label.setStyleSheet("color: black;")  # Set text color to black
        layout.addWidget(self.author_label)

        # Status Dropdown
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Unread", "In Progress", "Read"])
        self.status_dropdown.setCurrentText(book.status)
        self.status_dropdown.currentTextChanged.connect(
            lambda text, b=book: status_change_callback(b, text)
        )
        self.status_dropdown.setStyleSheet("""
            color: black; 
            background-color: #c87f4a;  /* Set background color to orange */
        """)
        layout.addWidget(self.status_dropdown)

        # Remove Button
        self.remove_button = QPushButton("Remove")
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #c87f4a;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #a66a40;
            }
        """)
        self.remove_button.clicked.connect(
            lambda checked, b=book: remove_callback(b)
        )
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

        # Enable hover effects
        self.setMouseTracking(True)


class CollectionPage(QWidget):
    def __init__(self, user, show_book_search_callback, logout_callback):
        super().__init__()

        self.current_status = "None"

        self.user = user
        self.show_book_search_callback = show_book_search_callback
        self.logout_callback = logout_callback

        # Image cache to prevent garbage collection
        self.book_images = {}

        # Setup UI
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Navigation layout
        nav_layout = QHBoxLayout()

        self.filter_options = QComboBox(self)
        self.filter_options.addItems(["None", "Unread", "In Progress", "Read"])
        self.filter_options.currentIndexChanged.connect(self.updateStatus)
        self.filter_options.setStyleSheet("""
            QComboBox {
                background-color: #c87f4a; 
                color: white; 
                padding: 10px;
                border-radius: 5px;
                font-family: Bahnschrift SemiBold;
                font-size: 12pt;
            }
            QComboBox:hover {
                background-color: #a66a40;
            }
            QListView {
                        background-color: #c87f4a;
            }
        """)

        #sort alphabetically by author or title
        self.alpha_sort = QComboBox(self)
        self.alpha_sort.addItems(["A-Z: Title", "A-Z: Author", "Z-A: Title", "Z-A: Author"])
        self.alpha_sort.currentIndexChanged.connect(self.update_alpha2)
        self.alpha_sort.setStyleSheet("""
                    QComboBox {
                        background-color: #c87f4a; 
                        color: white; 
                        padding: 10px;
                        border-radius: 5px;
                        font-family: Bahnschrift SemiBold;
                        font-size: 12pt;
                    }
                    QComboBox:hover {
                        background-color: #a66a40;
                    }
                    QListView {
                        background-color: #c87f4a;
                    }
                """)

        back_button = QPushButton("Back to Search")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #c87f4a; 
                color: white; 
                padding: 10px;
                border-radius: 5px;
                font-family: Bahnschrift SemiBold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #a66a40;
            }
        """)
        back_button.clicked.connect(self.show_book_search_callback)

        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #c87f4a; 
                color: white; 
                padding: 10px;
                border-radius: 5px;
                font-family: Bahnschrift SemiBold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #a66a40;
            }
        """)
        logout_button.clicked.connect(self.logout_callback)


        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by title or ISBN...")
        self.search_bar.textChanged.connect(self.filter_collection)
        self.search_bar.setStyleSheet("""
              QLineEdit {
                  background-color: #EAD2A8;
                  border: 2px solid #c87f4a;
                  border-radius: 5px;
                  padding: 5px;
                  color: black;
                  font-family: Bahnschrift SemiBold;
                  font-size: 12pt;
              }
        """)

        nav_layout.addWidget(back_button)
        nav_layout.addWidget(self.search_bar)
        nav_layout.addWidget(self.alpha_sort)
        nav_layout.addWidget(self.filter_options)
        nav_layout.addWidget(logout_button)
        main_layout.addLayout(nav_layout)

        # Scroll Area for Grid Layout
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #EAD2A8; border: none;")

        # Grid Widget
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)

        # Set scroll area widget
        self.scroll_area.setWidget(self.grid_widget)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        # No results label
        self.no_results_label = QLabel("No books found")
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.setStyleSheet("color: gray; font-size: 16px;")
        self.no_results_label.hide()
        main_layout.addWidget(self.no_results_label)

        # Display collection
        self.display_collection()

    def updateStatus(self, index):
        #["None", "Unread", "In Progress", "Read"]
        if index == 0:
            self.current_status = "None"
        if index == 1:
            self.current_status = "Unread"
        if index == 2:
            self.current_status = "In Progress"
        if index == 3:
            self.current_status = "Read"
        self.display_collection()

    def update_alpha2(self, index):
        #{"title": "title", "author": "author", "status": "status"}
        collection = load_collection(self.user.username)
        if index == 0:
            collection.sort_books(True, "title")
        elif index == 1:
            collection.sort_books(True, "author")
        elif index == 2:
            collection.sort_books(False, "title")
        elif index == 3:
            collection.sort_books(False, "author")
        save_collection(self.user.username, collection)
        self.display_collection()


    def display_collection(self, books=None,):
        current_status = self.current_status
        # print(self.current_status)        Used for debugging
        # Clear existing grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Load collection if not provided
        if books is None or books == False: #some weird typing issue comes up if False isn't here
            books = load_collection(self.user.username).to_list()

        # Show/hide no results label
        self.no_results_label.setVisible(len(books) == 0)

        # Calculate grid dimensions based on screen size
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()

        # Determine number of columns based on screen width
        columns = 3 if screen_width > 1600 else (2 if screen_width > 800 else 1)

        # Populate grid
        for idx, book in enumerate(books):
                   #show books matching the current status of collection
            if current_status == "None" or getattr(book, 'status') == current_status:
                row = idx // columns
                col = idx % columns

                # Get image path
                image_path = getattr(book, 'cover_image_path', None)

                # Create book card
                book_card = BookCard(
                    book,
                    image_path,
                    self.remove_book,
                    self.change_status
                )

                # Add to grid
                self.grid_layout.addWidget(book_card, row, col)

    def filter_collection(self, query):
        # Dynamically filter the collection based on search query
        # Load collection
        collection = load_collection(self.user.username)

        # Search books
        filtered_books = collection.search_books(query)

        # Display filtered books
        self.display_collection(filtered_books)

    def change_status(self, book, new_status):
        collection = load_collection(self.user.username)
        for b in collection:
            if b.isbn == book.isbn:
                b.status = new_status
                break
        save_collection(self.user.username, collection)

    def remove_book(self, book):
        collection = load_collection(self.user.username)
        collection.remove_book(book.isbn)
        save_collection(self.user.username, collection)
        self.display_collection()
