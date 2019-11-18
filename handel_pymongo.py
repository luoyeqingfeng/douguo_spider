import pymongo
from pymongo.collection import Collection

class Connect_mongo(object):
    def __init__(self):
        #创建数据库连接对象
        self.client=pymongo.MongoClient(host="127.0.0.1",port=27017)
        #生成操作的数据库对象
        self.db_data=self.client["dou_guo_mei_shi"]
    def insert_item(self,item):
        #创建集合集合对象
        myset=self.db_data["dou_guo_mei_shi_item"]
        #插入数据
        myset.insert_one(item)
        # db_collection=Collection(self.db_data,"dou_guo_mei_shi_item")
        # #插入数据
        # db_collection.insert_one(item)
mongo_info=Connect_mongo()