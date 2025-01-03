class Book:
    def __init__(self, title, author, isbn, cover_url=None, status="Unread", cover_image_path=None):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.cover_url = cover_url
        self.status = status
        self.cover_image_path = cover_image_path  # Add the cover_image_path attribute

    def __repr__(self):
        return f"Book({self.title}, {self.author}, {self.isbn}, {self.cover_url}, {self.status}, {self.cover_image_path})"

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "cover_url": self.cover_url,
            "status": self.status,
            "cover_image_path": self.cover_image_path  # Include cover_image_path in to_dict
        }

    def __eq__(self, other):
        if isinstance(other, Book):
            return self.isbn == other.isbn  # Compare books based on ISBN
        return False

    def __hash__(self):
        return hash(self.isbn)  # Use ISBN as the unique identifier for hashing
