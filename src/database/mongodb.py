import pymongo
import os
from dotenv import load_dotenv

import certifi
ca = certifi.where()

load_dotenv()
MONGO_DB_URL = os.getenv('MONGO_DB_URL')

class MongodbOperation:

    def __init__(self, db_name) -> None:

        self.client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
        self.db_name= db_name

    def insert_many(self,collection_name,records:list):
        self.client[self.db_name][collection_name].insert_many(records)

    def insert(self,collection_name,record):
        self.client[self.db_name][collection_name].insert_one(record)
        
