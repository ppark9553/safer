from pymongo import MongoClient

USER = "minestoned"
PW = "moneyisnoweverythingdawg"
IP = "45.55.86.183"
DB = "stock"

self.mongo = MongoClient("mongodb://{0}:{1}@{2}/{3}".format(user, password, ip_address, db_name))
