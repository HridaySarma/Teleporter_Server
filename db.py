from flask_pymongo import pymongo

client = pymongo.MongoClient(
    "mongodb+srv://teleporter:teleporter@cluster0.paoye.mongodb.net/teleporter?retryWrites=true&w=majority")

db = client.teleporter
user_collection = db.users


def hasAnUser(phone):
    global db
    query = {"phone": phone}
    return user_collection.count_documents(query) > 0


def findUserByPhone(phone):
    global db
    query = {"phone": phone}
    return user_collection.find(query)

def findUserById(user_id):
    global db
    query ={"user_id":user_id}
    return user_collection.find(query)

def getAllUser():
    global db
    return user_collection.find({})