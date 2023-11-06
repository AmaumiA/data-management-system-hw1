import threading
from datetime import datetime, timedelta
from be.model import error, db_conn


class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)  # 定时器每分钟执行一次
        print('第一次启动')
        self.cancel_timer.start()

    def cancel_unpaid_orders(self):
        try:
            new_order_collection = self.db["new_order"]
            current_time = datetime.now()
            time_interval = current_time - timedelta(minutes=1)

            unpaid_order_cursor = new_order_collection.find({"status": "unpaid"})
            for order in unpaid_order_cursor:
                order_time = datetime.fromisoformat(order["created_at"])
                if order_time < time_interval:
                    new_order_collection.update_one(
                        {"order_id": order["order_id"]},
                        {"$set": {"status": "cancelled"}}
                    )
        except Exception as e:
            print(f"Error canceling unpaid orders: {str(e)}")

        # 重新启动定时器
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)
        print('第二次启动')
        self.cancel_timer.start()


if __name__ == "__main__":
    order_auto_cancel = OrderAutoCancel()
