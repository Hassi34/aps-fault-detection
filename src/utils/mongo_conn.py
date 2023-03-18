import pymongo
import certifi
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.environ['MONGO_DB_URL']
MONGO_DATABSE_NAME = os.environ['MONGO_DATABASE_NAME']

ca = certifi.where()

class MongoDBClient:
    client = None
    def __init__(self, database_name=MONGO_DATABSE_NAME) -> None:
        try:
            if MongoDBClient.client is None:
                mongo_db_url  = MONGO_DB_URL
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name
        except Exception as e:
            raise e