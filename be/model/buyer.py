import uuid
import json
from datetime import datetime

import pymongo

from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
            self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                store_collection = self.db["store"]
                store_data = store_collection.find_one({"store_id": store_id, "book_id": book_id})
                if store_data is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = store_data["stock_level"]
                price = store_data["price"]

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                result = store_collection.update_one(
                    {"store_id": store_id, "book_id": book_id},
                    {"$inc": {"stock_level": -count}}
                )
                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                new_order_detail_collection = self.db["new_order_detail"]
                new_order_detail_collection.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })

            new_order_collection = self.db["new_order"]
            new_order_collection.insert_one({
                "user_id": user_id,
                "store_id": store_id,
                "order_id": uid,
                "status": "unpaid",
                "created_at": datetime.now().isoformat(),
                "shipped_at": None,
                "received_at": None
            })
            order_id = uid
        except BaseException as e:
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            new_order_collection = self.db["new_order"]
            order_data = new_order_collection.find_one({"order_id": order_id})
            if order_data is None:
                return error.error_invalid_order_id(order_id)
            if order_data["user_id"] != user_id:
                return error.error_authorization_fail()

            if order_data["status"] == "paid":
                return error.error_status_fail(order_id)

            if order_data["status"] == "shipped":
                return error.error_status_fail(order_id)
            user_collection = self.db["user"]
            user_data = user_collection.find_one({"user_id": user_id})
            if user_data is None:
                return error.error_non_exist_user_id(user_id)
            if password != user_data["password"]:
                return error.error_authorization_fail()
            balance = user_data["balance"]

            user_store_collection = self.db["user_store"]
            user_store_data = user_store_collection.find_one({"store_id": order_data["store_id"]})
            if user_store_data is None:
                return error.error_non_exist_store_id(order_data["store_id"])

            seller_id = user_store_data["user_id"]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            new_order_detail_collection = self.db["new_order_detail"]
            total_price = 0
            for order_detail in new_order_detail_collection.find({"order_id": order_id}):
                count = order_detail["count"]
                price = order_detail["price"]
                total_price += price * count
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            # 扣款，更新用户余额
            new_balance = balance - total_price
            result = user_collection.update_one(
                {"user_id": user_id},
                {"$set": {"balance": new_balance}}
            )
            if result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)
            # 更新订单状态为 "paid"
            new_order_collection.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": "paid"
                    }
                }
            )
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            new_order_collection = self.db["new_order"]
            order_data = new_order_collection.find_one({"order_id": order_id})
            if order_data is None:
                return error.error_invalid_order_id(order_id)

            if order_data["user_id"] != user_id:
                return error.error_authorization_fail()
            if order_data["status"] == "received":
                return 200, "Order is already received"
            if order_data["status"] != "shipped":
                return error.error_status_fail(order_id)

            # 更新订单状态为 "received" 并记录收货时间
            new_order_collection.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": "received",
                        "received_at": datetime.now().isoformat()
                    }
                }
            )
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user_collection = self.db["user"]
            user_data = user_collection.find_one({"user_id": user_id})
            if user_data is None:
                return error.error_authorization_fail()

            if user_data["password"] != password:
                return error.error_authorization_fail()

            result = user_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
            if result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def get_buyer_orders(self, user_id: str) -> (int, str, list):
        try:
            new_order_collection = self.db["new_order"]
            buyer_orders = []
            orders = new_order_collection.find({"user_id": user_id})
            for i in orders:
                buyer_orders.append(
                    {'store_id': i["store_id"],
                     'order_id': i["order_id"],
                     'status': i["status"]}
                )
            return 200, "ok", buyer_orders
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            new_order_collection = self.db["new_order"]
            order_data = new_order_collection.find_one({"order_id": order_id})

            if order_data is None:
                return error.error_invalid_order_id(order_id)
            if order_data["user_id"] != user_id:
                return error.error_authorization_fail()
            if order_data["status"] == "shipped" or order_data["status"] == "received":
                return error.error_status_fail(order_id)
            if order_data["status"] == "cancelled":
                return 200, "Order is already cancelled."
            if order_data["status"] == "paid":
                # 获取订单详细信息
                new_order_detail_collection = self.db["new_order_detail"]
                total_price = 0
                for order_detail in new_order_detail_collection.find({"order_id": order_id}):
                    count = order_detail["count"]
                    price = order_detail["price"]
                    total_price += price * count

                # 更新用户余额，将付款退还给用户
                user_collection = self.db["user"]
                user_data = user_collection.find_one({"user_id": user_id})
                if user_data is None:
                    return error.error_non_exist_user_id(user_id)

                # 计算退款金额
                refund_amount = total_price
                current_balance = user_data["balance"]
                new_balance = current_balance + refund_amount

                # 更新用户余额
                user_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"balance": new_balance}}
                )

            # 取消订单，更新状态为 "cancelled"
            new_order_collection.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": "cancelled"
                    }
                }
            )
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
