from pymongo import MongoClient

class MongoDB:

    def __init__(self, user, password, ip_address, db_name):
        self.mongo = MongoClient("mongodb://{0}:{1}@{2}/{3}".format(user, password, ip_address, db_name))
        self.collection = self.mongo[db_name].data

    def initialize(self, db_initializer):
        self.collection.insert_one(db_initializer)

    def add(self, code, data_key, data):
        # data has to be in an array
        self.collection.update_one(
            {"code": code},
            {"$set": {data_key: data}})

    def update(self, code, data_key, data):
        self.collection.update_one(
            {"code": code},
            {"$push": {data_key: data}})
