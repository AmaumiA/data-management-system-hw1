import logging
import os
import pymongo
import logging
import os



class Store:
    def __init__(self, host,port):
        self.client = pymongo.MongoClient(host,port)
        self.db = self.client["bookstore"]

    def init_tables(self):
        self.db['book'].create_index([
            ('id', pymongo.ASCENDING),
            ('title', 'text'),
            ('author', 'text'),
            ('publisher', 'text'),
            ('isbn', 'text'),
            ('content', 'text'),
            ('tags', 'text'),
            ('book_intro', 'text'),
        ],
            default_language="chinese",
            weights={'title': 2, 'author': 2, 'isbn': 2}
        )

    # def get_db_conn(self):
    #     pass
    #     # 不需要获取数据库连接，MongoDB 是服务器端数据库

database_instance: Store = None

def init_database(host,port):
    global database_instance
    database_instance = Store(host,port)

def get_db_conn():
    global database_instance
    return database_instance