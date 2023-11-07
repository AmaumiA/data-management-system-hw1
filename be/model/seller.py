import json
from datetime import datetime
import pymongo
from be.model import error
from be.model import db_conn
from base64 import b64decode
from bson.binary import Binary

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
            store_data = {
                "store_id": store_id,
                "book_id": book_id,
                "price" : json.loads(book_json_str)['price'],
                "stock_level": stock_level
            }

            # store_data = {
            #     "store_id": store_id,
            #     "book_id": book_id,
            #     "book_info": json.loads(book_json_str),
            #     "stock_level": stock_level
            # }


            store_collection.insert_one(store_data)

            book_collection = self.db["book"]

            book_data = json.loads(book_json_str)

            if not self.book_id_exist_in_all(book_data['id']):

                for key in list(book_data.keys()):

                    if key not in ["id", "title", "author", "publisher", "original_title", "translator", "pub_year",
                                   "pages", "price", "currency_unit", "binding", "isbn", "author_intro", "book_intro",
                                   "content", "tags","pictures"]:
                        book_data.pop(key)

                    pics=[]
                    if key=='pictures':
                        for pic in book_data['pictures']:
                            pics.append(Binary(b64decode(pic)))
                        book_data['pictures'] = pics

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


            new_order_collection = self.db["new_order"]
            seller_orders = []

            for store in seller_stores:
                orders = list(
                    new_order_collection.find({"store_id": store},{"_id":0})
                )
                for i in orders:
                    seller_orders.append(
                        {'store_id': i["store_id"],
                         'order_id': i["order_id"],
                         'status': i["status"]}
                    )

            return 200, "ok", seller_orders
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []