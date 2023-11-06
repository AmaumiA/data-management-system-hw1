import pymongo
from be.model import store


# class DBConn:
#     def __init__(self):
#         self.conn = store.get_db_conn()
#
#     def user_id_exist(self, user_id):
#         cursor = self.conn.execute(
#             "SELECT user_id FROM user WHERE user_id = ?;", (user_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
#
#     def book_id_exist(self, store_id, book_id):
#         cursor = self.conn.execute(
#             "SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;",
#             (store_id, book_id),
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
#
#     def store_id_exist(self, store_id):
#         cursor = self.conn.execute(
#             "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
#         )
#         row = cursor.fetchone()
#         if row is None:
#             return False
#         else:
#             return True
class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()
        self.db = self.conn.client['bookstore']

    def user_id_exist(self, user_id):
        user_collection = self.db["user"]
        user_doc = user_collection.find_one({"user_id": user_id})
        return user_doc is not None

    def book_id_exist(self, store_id, book_id):
        store_collection = self.db["store"]
        store_doc = store_collection.find_one({"store_id": store_id, "book_id": book_id})
        return store_doc is not None

    def store_id_exist(self, store_id):
        user_store_collection = self.db["user_store"]
        user_store_doc = user_store_collection.find_one({"store_id": store_id})
        return user_store_doc is not None

    def book_id_exist_in_all(self, book_id):
        store_collection = self.db["book"]
        store_doc = store_collection.find_one({"id": book_id})
        return store_doc is not None
