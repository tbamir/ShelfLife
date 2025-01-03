import os
import json
import bcrypt
import requests
from PIL import Image
from book import Book
from io import BytesIO
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from collection import Collection

# Set up base directory for user data in the current working directory
BASE_DIR = os.path.join(os.getcwd(), "user_data")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_user_directory(username):
    """Returns the directory where user data is stored (in user_data folder)."""
    return os.path.join(BASE_DIR, username)

def load_collection(username):
    """Loads the user's book collection from file."""
    user_directory = get_user_directory(username)
    collection_file = os.path.join(user_directory, "collection.json")
    
    if not os.path.exists(collection_file):
        return Collection()  # Return an empty Collection instance
    
    try:
        with open(collection_file, "r") as file:
            books_data = json.load(file)
            collection = Collection()
            for book_data in books_data:
                collection.add_book(
                    Book(
                        title=book_data.get("title"),
                        author=book_data.get("author"),
                        isbn=book_data.get("isbn"),
                        cover_image_path=book_data.get("cover_image_path"),
                        cover_url=book_data.get("cover_url"),
                        status=book_data.get("status", "Unread")
                    )
                )
            return collection
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading collection for user {username}: {e}")
        return Collection()

def save_collection(username, collection):
    """Saves the user's book collection to file."""
    user_directory = get_user_directory(username)
    
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
    
    collection_file = os.path.join(user_directory, "collection.json")
    books_data = [book.to_dict() for book in collection]
    
    try:
        with open(collection_file, "w") as file:
            json.dump(books_data, file, indent=4)
    except IOError as e:
        print(f"Error saving collection for user {username}: {e}")

def load_wishlist(username):
    """Loads the user's book wishlist from file."""
    user_directory = get_user_directory(username)
    collection_file = os.path.join(user_directory, "wishlist.json")
    
    if not os.path.exists(collection_file):
        return Collection()  # Return an empty Collection instance
    
    try:
        with open(collection_file, "r") as file:
            books_data = json.load(file)
            collection = Collection()
            for book_data in books_data:
                collection.add_book(
                    Book(
                        title=book_data.get("title"),
                        author=book_data.get("author"),
                        isbn=book_data.get("isbn"),
                        cover_image_path=book_data.get("cover_image_path"),
                        cover_url=book_data.get("cover_url"),
                        status=book_data.get("status", "Unread")
                    )
                )
            return collection
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading wishlist for user {username}: {e}")
        return


def save_wishlist(username, wishlist):
    """Saves the user's book wishlist to file."""
    user_directory = get_user_directory(username)
    
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
    
    collection_file = os.path.join(user_directory, "wishlist.json")
    books_data = [book.to_dict() for book in wishlist]
    
    try:
        with open(collection_file, "w") as file:
            json.dump(books_data, file, indent=4)
    except IOError as e:
        print(f"Error saving collection for user {username}: {e}")

def save_user_data(username, password, collection):
    """Saves the user's username, password (hashed), and collection to user_data folder."""
    user_directory = get_user_directory(username)
    
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
    
    try:
        # Save hashed password
        password_file = os.path.join(user_directory, "password.json")
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        with open(password_file, "w") as file:
            json.dump({"password": hashed_password}, file)
        
        # Save book collection
        save_collection(username, collection)
    except IOError as e:
        print(f"Error saving user data for {username}: {e}")

def load_user_password(username):
    """Loads the user's hashed password."""
    password_file = os.path.join(get_user_directory(username), "password.json")
    
    if not os.path.exists(password_file):
        return None  # No password file found
    
    try:
        with open(password_file, "r") as file:
            data = json.load(file)
            return data.get("password")
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading password for user {username}: {e}")
        return None

def register_user(username, password, collection=None):
    """Registers a new user by saving the username, password, and collection."""
    if os.path.exists(get_user_directory(username)):
        return False  # Username already exists
    
    collection = collection or Collection()  # Initialize an empty collection if none provided
    save_user_data(username, password, collection)
    return True

def login_user(username, password):
    """Attempts to log in the user by checking the hashed password."""
    stored_password = load_user_password(username)
    
    if stored_password is None:
        return False  # User not found
    
    return bcrypt.checkpw(password.encode(), stored_password.encode())

def save_image_locally(image_url, isbn):
    """Saves the book cover image locally from a URL."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img_data = BytesIO(response.content)
        image = Image.open(img_data)

        # Create a directory for storing images if it doesn't exist
        image_dir = os.path.join(BASE_DIR, "user_images")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        # Save the image
        image_path = os.path.join(image_dir, f"{isbn}.jpg")
        image.save(image_path)
        return image_path
    except requests.RequestException as e:
        print(f"Error fetching image for ISBN {isbn}: {e}")
    except IOError as e:
        print(f"Error saving image locally for ISBN {isbn}: {e}")
    return None

def display_collection(username, collection):
    """Displays the user's book collection in the GUI."""
    for book in collection:
        cover_image_path = book.cover_image_path
        if cover_image_path and os.path.exists(cover_image_path):
            img = QPixmap(cover_image_path)
        else:
            img = QPixmap(100, 150)
            img.fill(Qt.gray)
        # Logic for displaying images in the GUI should be implemented hereimport os