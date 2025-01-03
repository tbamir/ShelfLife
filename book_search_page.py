from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QFrame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
from book import Book
from storage import load_collection, save_collection, load_wishlist, save_wishlist, save_image_locally
from scanner import Scanner

class BookSearchPage(QWidget):
    def __init__(self, user, show_collection_callback, show_wishlist_callback, logout_callback):
        super().__init__()

        self.user = user
        self.show_collection_callback = show_collection_callback
        self.show_wishlist_callback = show_wishlist_callback
        self.logout_callback = logout_callback

        self.setWindowTitle("Book Search")
        self.setGeometry(100, 100, 1000, 700)

        # Main layout
        main_layout = QVBoxLayout()

        # Top section for the logo and logout button
        top_layout = QHBoxLayout()
        self.logo_label = QLabel("Shelf Life Book Manager")
        self.logo_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(self.logo_label, alignment=Qt.AlignLeft)

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout_callback)
        self.logout_button.setStyleSheet("margin-left: auto;")
        top_layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        main_layout.addLayout(top_layout)

        # Middle section with sidebar and result display
        middle_layout = QHBoxLayout()

        # Sidebar for buttons
        self.sidebar = QVBoxLayout()
        self.sidebar.setContentsMargins(10, 10, 10, 10)

        button_style = (
            "padding: 15px; font-size: 16px; font-weight: bold; background-color: #c87f4a; border-radius: 5px; "
            "border: 1px solid #ccc; margin-bottom: 10px;"
        )

        self.manual_button = QPushButton("New Search")
        self.manual_button.setStyleSheet(button_style)
        self.manual_button.clicked.connect(self.manual_entry)
        self.sidebar.addWidget(self.manual_button)

        
        self.scan_button = QPushButton("Scan Barcode")
        self.scan_button.setStyleSheet(button_style)
        self.scan_button.clicked.connect(self.scan_barcode)
        self.sidebar.addWidget(self.scan_button)
        
        
        self.view_collection_button = QPushButton("View Collection")
        self.view_collection_button.setStyleSheet(button_style)
        self.view_collection_button.clicked.connect(self.show_collection_callback)
        self.sidebar.addWidget(self.view_collection_button)

        self.view_wishlist_button = QPushButton("View Wishlist")
        self.view_wishlist_button.setStyleSheet(button_style)
        self.view_wishlist_button.clicked.connect(self.show_wishlist_callback)
        self.sidebar.addWidget(self.view_wishlist_button)

        # Spacer to push buttons to the top
        self.sidebar.addStretch()
        middle_layout.addLayout(self.sidebar, stretch=1)

        # Frame for displaying results
        self.result_frame = QFrame()
        self.result_frame.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px;")
        self.result_layout = QVBoxLayout(self.result_frame)
        middle_layout.addWidget(self.result_frame, stretch=3)

        main_layout.addLayout(middle_layout)
        self.setLayout(main_layout)

        # Initialize placeholders for dynamic elements
        self.isbn_entry = None
        self.add_button = None
        self.book_data = None
        self.status_dropdown = None

    def scan_barcode(self):
        isbn = Scanner.scan()
        if isbn is None:
            QMessageBox.information(self, "Scan Cancelled", "No barcode was scanned.")
            return  # Exit the method if no barcode is scanned.
        
        self.search_book(isbn)

    def manual_entry(self):
        # Clear previous search results
        self.clear_result_layout()

        self.isbn_entry = QLineEdit(self.result_frame)
        self.isbn_entry.setPlaceholderText("Enter ISBN or Title")
        self.result_layout.addWidget(self.isbn_entry)

        self.search_button = QPushButton("Search", self.result_frame)
        self.search_button.clicked.connect(lambda: self.search_book(self.isbn_entry.text().strip()))
        self.result_layout.addWidget(self.search_button)

    def clear_result_layout(self):
        for i in reversed(range(self.result_layout.count())):
            widget = self.result_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def search_book(self, query):
        # Validate the query before proceeding
        if not query:
            QMessageBox.warning(self, "Invalid Query", "Please enter a valid ISBN or title.")
            return

        # Clear previous search results
        self.clear_result_layout()

        # Try multiple methods to fetch book data and cover image
        book_data = self.fetch_book_data_with_cover(query)

        if book_data:
            self.book_data = book_data
            self.display_book_details(book_data)
        else:
            self.result_layout.addWidget(QLabel("No book found with this query."))

    def fetch_book_data_with_cover(self, query):
        """
        Comprehensive method to fetch book data with cover image from multiple sources.
        Attempts to retrieve data and cover from both Open Library and Google Books APIs.
        """
        # Ensure the query is valid
        if not query or not isinstance(query, str):
            QMessageBox.warning(self, "Invalid Query", "The query must be a non-empty string.")
            return None

        query = query.strip()  # Remove leading/trailing spaces

        book_data = None

        # First, attempt to fetch data by ISBN
        if query.isdigit():
            # Try Open Library first for ISBN
            book_data = self.query_open_library(query)

            # If Open Library fails, try Google Books
            if not book_data or not book_data.get('cover_url'):
                book_data = self.query_google_books(query)

        # If query is not an ISBN (title search)
        else:
            # Try Open Library title search first
            book_data = self.query_open_library(query)

            # If Open Library fails, try Google Books
            if not book_data or not book_data.get('cover_url'):
                book_data = self.query_google_books(query)

        # If still no book data, return None
        return book_data


    def query_open_library(self, query):
        try:
            if query.isdigit():
                # ISBN-specific query
                url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{query}&format=json&jscmd=data"
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if f"ISBN:{query}" in data:
                        book_info = data[f"ISBN:{query}"]
                        cover_urls = [
                            f"https://covers.openlibrary.org/b/isbn/{query}-L.jpg",
                            f"https://covers.openlibrary.org/b/isbn/{query}-M.jpg",
                            f"https://covers.openlibrary.org/b/isbn/{query}-S.jpg"
                        ]
                        
                        # Find a working cover URL
                        cover_url = next((url for url in cover_urls if self.validate_image_url(url)), None)
                        
                        return {
                            'title': book_info.get('title', 'No Title Available'),
                            'author': ', '.join(author['name'] for author in book_info.get('authors', [{'name': 'Unknown Author'}])),
                            'isbn': query,
                            'cover_url': cover_url
                        }
            
            else:
                # Title search
                url = f"https://openlibrary.org/search.json?title={query}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('docs'):
                        first_result = data['docs'][0]
                        
                        # Try to find ISBN for cover image
                        if 'isbn' in first_result and first_result['isbn']:
                            isbn = first_result['isbn'][0]
                            cover_urls = [
                                f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg",
                                f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg",
                                f"https://covers.openlibrary.org/b/isbn/{isbn}-S.jpg"
                            ]
                            
                            # Find a working cover URL
                            cover_url = next((url for url in cover_urls if self.validate_image_url(url)), None)
                            
                            return {
                                'title': first_result.get('title', 'No Title Available'),
                                'author': ', '.join(first_result.get('author_name', ['Unknown Author'])),
                                'isbn': first_result.get('isbn', [''])[0],
                                'cover_url': cover_url
                            }
        except Exception as e:
            print(f"Open Library API Error: {e}")
        
        return None

    def query_google_books(self, query):
        try:
            if query.isdigit():
                url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{query}"
            else:
                url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and len(data["items"]) > 0:
                    volume_info = data["items"][0]["volumeInfo"]
                    
                    # Prioritize larger images, replace 'zoom=1' with 'zoom=0' for higher resolution
                    cover_urls = [
                        volume_info.get('imageLinks', {}).get('extraLarge'),
                        volume_info.get('imageLinks', {}).get('large'),
                        volume_info.get('imageLinks', {}).get('medium'),
                        volume_info.get('imageLinks', {}).get('small'),
                        volume_info.get('imageLinks', {}).get('thumbnail')
                    ]
                    
                    # Remove None values and replace 'zoom=1' with 'zoom=0' for higher resolution
                    cover_urls = [
                        url.replace('zoom=1', 'zoom=0') if url else None 
                        for url in cover_urls if url
                    ]
                    
                    # Find a working cover URL
                    cover_url = next((url for url in cover_urls if self.validate_image_url(url)), None)

                    return {
                        'title': volume_info.get('title', 'No Title Available'),
                        'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                        'isbn': volume_info.get('industryIdentifiers')[0].get('identifier'),
                        'cover_url': cover_url
                    }
        except Exception as e:
            print(f"Google Books API Error: {e}")
        
        return None

    def validate_image_url(self, url):
        """
        Validate that the image URL is accessible and returns a valid image.
        """
        if not url:
            return False
        
        try:
            response = requests.head(url, timeout=5)
            return (
                response.status_code == 200 and 
                'image' in response.headers.get('Content-Type', '').lower()
            )
        except Exception:
            return False

    def display_book_details(self, book_data):
        self.result_layout.addWidget(QLabel(f"Title: {book_data['title']}"))
        self.result_layout.addWidget(QLabel(f"Author: {book_data['author']}"))
        self.result_layout.addWidget(QLabel(f"ISBN: {book_data['isbn']}"))

        try:
            if book_data['cover_url']:
                response = requests.get(book_data["cover_url"], stream=True)
                if response.status_code == 200:
                    image_data = QPixmap()
                    image_data.loadFromData(response.content)
                    cover_label = QLabel(self.result_frame)
                    cover_label.setPixmap(image_data.scaled(200, 300, Qt.KeepAspectRatio))
                    self.result_layout.addWidget(cover_label)
                else:
                    self.result_layout.addWidget(QLabel("Cover image could not be loaded"))
            else:
                self.result_layout.addWidget(QLabel("No cover image available"))
        except Exception as e:
            self.result_layout.addWidget(QLabel("Error loading cover image"))
            print("Error loading image:", e)

        # Add status dropdown for the user to select
        self.status_dropdown = QComboBox(self.result_frame)
        self.status_dropdown.addItems(["Unread", "In Progress", "Read"])
        self.result_layout.addWidget(self.status_dropdown)

        self.add_button = QPushButton("Add to Collection", self.result_frame)
        self.add_button.clicked.connect(self.add_to_collection)
        self.result_layout.addWidget(self.add_button)

        self.add_button = QPushButton("Add to Wishlist", self.result_frame)
        self.add_button.clicked.connect(self.add_to_wishlist)
        self.result_layout.addWidget(self.add_button)
        

    def add_to_collection(self):
        # Load the user's current collection
        collection = load_collection(self.user.username)

        # Check for duplicate book based on ISBN
        if any(book.isbn == self.book_data['isbn'] for book in collection.books):
            # Display a pop-up message informing the user about the duplicate
            QMessageBox.warning(
                self, 
                "Duplicate Book", 
                "This book is already in your collection.\n\n"
                "You cannot add the same book twice.",
                QMessageBox.Ok
            )
            return  # Exit the method without adding the book

        # If no duplicate is found, proceed with adding the book
        # Save the cover image locally when adding the book to the collection
        if self.book_data and 'cover_url' in self.book_data and self.book_data['cover_url']:
            try:
                cover_image_path = save_image_locally(self.book_data["cover_url"], self.book_data['isbn'])
                if cover_image_path:
                    self.book_data['cover_image_path'] = cover_image_path
                else:
                    self.result_layout.addWidget(QLabel("Cover image could not be saved"))
            except Exception as e:
                self.result_layout.addWidget(QLabel("Error saving cover image"))
                print("Error saving image:", e)

        # Filter the book data for saving
        book_data_filtered = {
            key: self.book_data[key]
            for key in ['title', 'author', 'isbn', 'cover_image_path']
            if key in self.book_data
        }

        # Get the selected status from the dropdown
        book_data_filtered["status"] = self.status_dropdown.currentText()

        # Create a Book object and add it to the user's collection
        book = Book(**book_data_filtered)
        collection.add_book(book)
        save_collection(self.user.username, collection)

        QMessageBox.information(self, "Success", "Book added to collection successfully!")

    def add_to_wishlist(self):
        # Load the user's current wishlist
        wishlist = load_wishlist(self.user.username)

        # Check for duplicate book based on ISBN
        if any(book.isbn == self.book_data['isbn'] for book in wishlist.books):
            # Display a pop-up message informing the user about the duplicate
            QMessageBox.warning(
                self, 
                "Duplicate Book", 
                "This book is already in your wishlist.\n\n"
                "You cannot add the same book twice.",
                QMessageBox.Ok
            )
            return  # Exit the method without adding the book

        # If no duplicate is found, proceed with adding the book
        # Save the cover image locally when adding the book to the collection
        if self.book_data and 'cover_url' in self.book_data and self.book_data['cover_url']:
            try:
                cover_image_path = save_image_locally(self.book_data["cover_url"], self.book_data['isbn'])
                if cover_image_path:
                    self.book_data['cover_image_path'] = cover_image_path
                else:
                    self.result_layout.addWidget(QLabel("Cover image could not be saved"))
            except Exception as e:
                self.result_layout.addWidget(QLabel("Error saving cover image"))
                print("Error saving image:", e)

        # Filter the book data for saving
        book_data_filtered = {
            key: self.book_data[key]
            for key in ['title', 'author', 'isbn', 'cover_image_path']
            if key in self.book_data
        }

        # Get the selected status from the dropdown
        book_data_filtered["status"] = self.status_dropdown.currentText()

        # Create a Book object and add it to the user's collection
        book = Book(**book_data_filtered)
        wishlist.add_book(book)
        save_wishlist(self.user.username, wishlist)

        QMessageBox.information(self, "Success", "Book added to wishlist successfully!")
