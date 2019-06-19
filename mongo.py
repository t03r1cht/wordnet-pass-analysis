from pymongo import MongoClient

mongo = MongoClient("mongodb://localhost:27017")
db = mongo["passwords"]
db_ill = db["ill"]
db_pws = db["passwords"]

