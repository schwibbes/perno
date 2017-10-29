from pymongo import MongoClient
client = MongoClient("mongodb://192.168.99.100:27017")
db = client["test"]

db.notes.delete_many({})
print db.notes.count()