import os
import random
import base64
import simplejson as json
from urllib.parse import urljoin
import requests
from fe import conf
from pymongo import MongoClient

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: str
    pictures: [bytes]

    def __init__(self):
        self.pictures = []


def search_in_store(store_id,title,author,publisher,isbn,content,tags,book_intro,page=1,per_page=10):
    json ={
            'store_id':store_id,
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'content': content,
            'tags': tags,
            'book_intro': book_intro,
            'page': page,
            "per_page": per_page
        }
    url = urljoin(urljoin(conf.URL, "book/"), "search_in_store")
    r = requests.post(url, json=json)
    return r.status_code,r.json()

def search_all(title,author,publisher,isbn,content,tags,book_intro,page=1,per_page=10):
    json ={
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'content': content,
            'tags': tags,
            'book_intro': book_intro,
            'page': page,
            "per_page": per_page
        }
    url = urljoin(urljoin(conf.URL, "book/"), "search_all")
    r = requests.post(url, json=json)
    return r.status_code,r.json()

class BookDB:
    def __init__(self, large: bool = False):
        self.client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection URL
        self.db = self.client['bookstore']  # Replace with your MongoDB database name
        if not large:
            self.collection = self.db['book']
        else:
            self.collection = self.db['book_lx']

    def get_book_count(self):
        return self.collection.count_documents({})

    def get_book_info(self, start, size):
        books = []
        cursor = self.collection.find({}).skip(start).limit(size)
        for row in cursor:
            book = Book()
            book.id = row['id']
            book.title = row['title']
            book.author = row['author']
            book.publisher = row['publisher']
            book.original_title = row['original_title']
            book.translator = row['translator']
            book.pub_year = row['pub_year']
            book.pages = row['pages']
            book.price = row['price']
            book.binding = row['binding']
            book.isbn = row['isbn']
            book.author_intro = row['author_intro']
            book.book_intro = row['book_intro']
            book.content = row['content']
            book.tags = row['tags']
            book.pictures = []
            pictures = row['pictures']
            # for i in range(0, random.randint(0, 9)):
            for picture in pictures:
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)
            books.append(book)
        return books

