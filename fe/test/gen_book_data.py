import random  # 导入 'random' 模块以生成随机数。
from fe.access import book  # 从 'fe.access' 包中导入 'book' 模块。
from fe.access.new_seller import register_new_seller  # 从 'fe.access.new_seller' 包中导入 'register_new_seller' 函数。
from fe import conf

# 创建一个名为 'GenBook' 的类，用于生成要购买的书籍列表。
class GenBook:
    def __init__(self, user_id, store_id):
        # 使用给定的 user_id 和 store_id 初始化 'GenBook' 类。
        self.user_id = user_id
        self.store_id = store_id
        self.password = self.user_id  # 将密码设置为与用户ID相同。
        self.seller = register_new_seller(self.user_id, self.password)  # 使用提供的 user_id 和密码注册一个新卖家。
        code = self.seller.create_store(store_id)  # 为卖家创建一个商店。
        assert code == 200  # 确保商店创建成功（HTTP 状态码为200）。
        self.__init_book_list__()  # 初始化书籍列表。

    def __init_book_list__(self):
        # 初始化两个空列表，用于存储书籍信息和要购买的书籍ID。
        self.buy_book_info_list = []
        self.buy_book_id_list = []

    def gen(
        self, non_exist_book_id: bool, low_stock_level, max_book_count: int = 100
    ) -> (bool, []):
        # 根据指定的参数生成要购买的书籍列表。
        self.__init_book_list__()  # 重新初始化书籍列表。
        ok = True  # 初始化一个名为 'ok' 的标志为True。
        book_db = book.BookDB(conf.Use_Large_DB)  # 创建一个数据库连接以访问书籍信息。
        rows = book_db.get_book_count()  # 获取数据库中的总书籍数量。
        start = 0

        # 如果可用书籍数量超过最大允许值，则选择一个随机起始点。
        if rows > max_book_count:
            start = random.randint(0, rows - max_book_count)

        size = random.randint(1, max_book_count)  # 随机确定要选择的书籍数量。
        books = book_db.get_book_info(start, size)  # 从数据库中检索书籍信息。

        book_id_exist = []  # 初始化一个列表，用于存储已存在的书籍ID。
        book_id_stock_level = {}  # 初始化一个字典，用于存储书籍ID和它们的库存水平。

        for bk in books:
            if low_stock_level:
                stock_level = random.randint(0, 100)  # 生成随机库存水平（低）。
            else:
                stock_level = random.randint(2, 100)  # 生成随机库存水平（至少为2）。
            code = self.seller.add_book(self.store_id, stock_level, bk)  # 使用指定的库存水平将书籍添加到商店。
            assert code == 200  # 确保书籍添加成功（HTTP 状态码为200）。
            book_id_stock_level[bk.id] = stock_level  # 存储书籍ID和库存水平。
            book_id_exist.append(bk)  # 将书籍添加到已存在书籍列表中。

        for bk in book_id_exist:
            stock_level = book_id_stock_level[bk.id]
            if stock_level > 1:
                buy_num = random.randint(1, stock_level)  # 在可用库存内生成要购买的书籍数量。
            else:
                buy_num = 0  # 如果库存水平小于等于1，则不购买该书籍。

            # 可选地，通过在现有书籍ID末尾添加 "_x" 来添加一个新的书籍ID。
            if non_exist_book_id:
                bk.id = bk.id + "_x"

            # 如果 'low_stock_level' 为True，将 'buy_num' 设置为大于可用库存。
            if low_stock_level:
                buy_num = stock_level + 1

            # 将书籍和购买的副本数量添加到要购买的书籍列表中。
            self.buy_book_info_list.append((bk, buy_num))

        for item in self.buy_book_info_list:
            self.buy_book_id_list.append((item[0].id, item[1]))  # 创建一个书籍ID和相应购买数量的列表。

        return ok, self.buy_book_id_list  # 返回 'ok' 标志和要购买的书籍列表。
