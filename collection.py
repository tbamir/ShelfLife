
class Collection:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        # Adds a book to the collection.
        # Prevents duplicate books based on ISBN.
        if not any(existing_book.isbn == book.isbn for existing_book in self.books):
            self.books.append(book)
            return True
        return False

    def remove_book(self, isbn):
        # Removes a book from the collection by its ISBN.
        self.books = [book for book in self.books if book.isbn != isbn]

    def to_list(self):
        # Returns the list of books in the collection.
        return self.books

    def __iter__(self):
        # Makes the collection iterable.
        return iter(self.books)

    def get_book_by_isbn(self, isbn):
        # Retrieve a book by its ISBN.
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None

    def sort_books(self, alpha ,choice = "title"):
        """Sorts books in the collection by a given attribute: title, author, or status."""
        valid_keys = {"title": "title", "author": "author", "status": "status"}
        if choice not in valid_keys:
            raise ValueError(f"Invalid sort key '{choice}'. Must be one of {list(valid_keys.keys())}.")

        if alpha == True:
            self.books.sort(key=lambda book: "".join(filter(str.isalpha, (getattr(book, valid_keys[choice])))))
        if alpha == False:
            self.books.sort(key=lambda book: "".join(filter(str.isalpha, (getattr(book, valid_keys[choice])))))
            self.books.reverse()
        #print(f"Books sorted by {choice}.")        Used for debugging

    def search_books(self, query):
        if not query:
            return self.books

        query = query.lower().strip()
        return [
            book for book in self.books
            if query in book.title.lower() or query in book.isbn.lower()
        ]
