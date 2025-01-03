from collection import Collection
from wishlist import Wishlist

class User:
    def __init__(self, username):
        self.username = username
        self.collection = Collection()
        self.wishlist = Wishlist()