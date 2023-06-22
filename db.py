from pymongo import MongoClient

def get_db(db_name: str):
    client = MongoClient('localhost', 27017)
    db = client["bludv"]
    return db[db_name]


