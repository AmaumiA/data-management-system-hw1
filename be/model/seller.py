import json
from datetime import datetime

# class Seller(db_conn.DBConn):
#     def __init__(self):
#         db_conn.DBConn.__init__(self)
#
#     def add_book(
#         self,
#         user_id: str,
#         store_id: str,
#         book_id: str,
#         book_json_str: str,
#         stock_level: int,
#     ):
#         try:
#             if not self.user_id_exist(user_id):
#                 return error.error_non_exist_user_id(user_id)
#             if not self.store_id_exist(store_id):
#                 return error.error_non_exist_store_id(store_id)
#             if self.book_id_exist(store_id, book_id):
#                 return error.error_exist_book_id(book_id)
#
#             self.conn.execute(
#                 "INSERT into store(store_id, book_id, book_info, stock_level)"
#                 "VALUES (?, ?, ?, ?)",
#                 (store_id, book_id, book_json_str, stock_level),
#             )
#             self.conn.commit()
#         except sqlite.Error as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"
#
#     def add_stock_level(
#         self, user_id: str, store_id: str, book_id: str, add_stock_level: int
#     ):
#         try:
#             if not self.user_id_exist(user_id):
#                 return error.error_non_exist_user_id(user_id)
#             if not self.store_id_exist(store_id):
#                 return error.error_non_exist_store_id(store_id)
#             if not self.book_id_exist(store_id, book_id):
#                 return error.error_non_exist_book_id(book_id)
#
#             self.conn.execute(
#                 "UPDATE store SET stock_level = stock_level + ? "
#                 "WHERE store_id = ? AND book_id = ?",
#                 (add_stock_level, store_id, book_id),
#             )
#             self.conn.commit()
#         except sqlite.Error as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"
#
#     def create_store(self, user_id: str, store_id: str) -> (int, str):
#         try:
#             if not self.user_id_exist(user_id):
#                 return error.error_non_exist_user_id(user_id)
#             if self.store_id_exist(store_id):
#                 return error.error_exist_store_id(store_id)
#             self.conn.execute(
#                 "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
#                 (store_id, user_id),
#             )
#             self.conn.commit()
#         except sqlite.Error as e:
#             return 528, "{}".format(str(e))
#         except BaseException as e:
#             return 530, "{}".format(str(e))
#         return 200, "ok"


import pymongo
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            book_json_str: str,
            stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            store_collection = self.db["store"]
            # store_data = {
            #     "store_id": store_id,
            #     "book_id": book_id,
            #     "stock_level": stock_level
            # }

            store_data = {
                "store_id": store_id,
                "book_id": book_id,
                # "book_info": json.loads(book_json_str),
                "stock_level": stock_level
            }
            # print(1)
            store_collection.insert_one(store_data)
            # print(2)
            book_collection = self.db["book"]
            # print(book_json_str)
            # print(type(book_json_str))
            book_data = json.loads(book_json_str)
            # print(3)

            for key in list(book_data.keys()):
                # print(key)
                if key not in ["id", "title", "author", "publisher", "original_title", "translator", "pub_year",
                               "pages", "price", "currency_unit", "binding", "isbn", "author_intro", "book_intro",
                               "content", "tags"]:
                    book_data.pop(key)
            # print(5)

            book_collection.insert_one(book_data)


        except pymongo.errors.DuplicateKeyError:
            return error.error_exist_book_id(book_id)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
            self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            store_collection = self.db["store"]
            store_collection.update_one(
                {"store_id": store_id, "book_id": book_id},
                {"$inc": {"stock_level": add_stock_level}}
            )
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            user_store_collection = self.db["user_store"]
            user_store_data = {
                "store_id": store_id,
                "user_id": user_id
            }
            user_store_collection.insert_one(user_store_data)
        except pymongo.errors.DuplicateKeyError:
            return error.error_exist_store_id(store_id)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def ship_order(self, store_id: str, order_id: str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            new_order_collection = self.db["new_order"]
            order_data = new_order_collection.find_one({"order_id": order_id})

            if order_data is None:
                return error.error_invalid_order_id(order_id)

            if order_data["store_id"] != store_id:
                return error.error_authorization_fail()

            if order_data["status"] == "shipped":
                return 200, "Order is already shipped."

            if order_data["status"] != "paid":
                return error.error_status_fail(order_id)

            # 更新订单状态为 "shipped" 并记录发货时间
            new_order_collection.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": "shipped",
                        "shipped_at": datetime.now().isoformat()
                    }
                }
            )
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def get_seller_orders(self, user_id: str) -> (int, str, list):
        try:
            user_store_collection = self.db["user_store"]
            seller_stores = [store["store_id"] for store in user_store_collection.find({"user_id": user_id})]

            # print(seller_stores)

            new_order_collection = self.db["new_order"]
            seller_orders = []

            for store in seller_stores:
                orders = list(
                    new_order_collection.find({"store_id": store},{"_id":0})
                )
                print(orders)
                seller_orders.extend(orders)

            return 200, "ok", seller_orders
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []