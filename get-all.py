from pymongo import MongoClient
client = MongoClient("mongodb://192.168.99.100:27017")
db = client["test"]

#result = db.notes.insert_one( { "title":  "1st" } )
#db.notes.delete_many({})
for x in db.notes.find():
	print x
print db.notes.count()