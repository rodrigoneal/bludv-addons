from pymongo import MongoClient

from src.schemas.movie_schema import Filme


client = MongoClient('localhost', 27017)
db = client["bludv"]
db_collection = db["movies"]
cursores = db_collection.find({})
Filme
breakpoint()

