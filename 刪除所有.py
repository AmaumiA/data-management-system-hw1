# 连接到MongoDB数据库
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["bookstore"]  # 选择你的数据库名，这里使用"bookstore"

# 获取数据库中的所有集合
collections = db.list_collection_names()

# 遍历并删除每个集合
for collection_name in collections:
    db.drop_collection(collection_name)

print("所有集合已删除")
