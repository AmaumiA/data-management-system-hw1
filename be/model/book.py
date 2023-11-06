import pymongo
import uuid
import json
import logging
from be.model import error
from be.model import db_conn

class Book(db_conn.DBConn):
    # ... 你现有的代码 ...
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # def search_all(self,title,author,publisher,isbn,content,tags,book_intro):
    def search_in_store(self,store_id,title,author,publisher,isbn,content,tags,book_intro):
        try:
            # print('aaaaaaaaaaaaaa')
            store_collection = self.db["store"]
            book_collection = self.db["book"]

            query={'store_id':store_id}
            res = store_collection.find(query, {"book_id": 1, "book_info": 1, "_id": 0})
            ids=[]
            for i in res:
                ids+=list(i.values())
            print(ids)

            qs_dict={
                'title': title,
                'author': author,
                'publisher': publisher,
                'isbn': isbn,
                'content': content,
                'tags': tags,
                'book_intro': book_intro
            }
            qs_dict1={}
            for key,value in qs_dict.items():
                if len(value)!=0:
                    qs_dict1[key]=value
            qs_dict=qs_dict1
            # print(qs_dict)
            qs_list=[{key:{"$regex": value}} for key,value in qs_dict.items()]
            # print(qs_list)
            query = {
                "$and": [
                    {"id": {"$in": ids}},
                ]+qs_list
            }
            # print(query)
            # 使用 find 方法执行查询
            result = book_collection.find(query,{'_id':0})
            result = [i for i in result]
            print(result)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))


        return 200,result

    def search_all(self,title,author,publisher,isbn,content,tags,book_intro):
        try:
            book_collection = self.db["book"]

            qs_dict={
                'title': title,
                'author': author,
                'publisher': publisher,
                'isbn': isbn,
                'content': content,
                'tags': tags,
                'book_intro': book_intro
            }
            qs_dict1={}
            for key,value in qs_dict.items():
                if len(value)!=0:
                    qs_dict1[key]=value
            qs_dict=qs_dict1
            # print(qs_dict)
            qs_list=[{key:{"$regex": value}} for key,value in qs_dict.items()]
            # print(qs_list)
            query = {
                "$and": qs_list
            }
            # print(query)
            # 使用 find 方法执行查询
            result = book_collection.find(query,{'_id':0})
            result = [i for i in result]
            print(result)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))


        return 200,result
