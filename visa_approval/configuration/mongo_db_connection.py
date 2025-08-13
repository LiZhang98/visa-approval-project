import sys

from visa_approval.exception import USvisaException
from visa_approval.logger import logging

import os
from visa_approval.constants import DATABASE_NAME, MONGODB_URL_KEY
import pymongo
import certifi

ca = certifi.where()

class MongoDBClient:
    
    client = None
    
    def __init__(self, database_name=DATABASE_NAME) -> None:
        
        try:
            if MongoDBClient.client is None:
                mongo_db_url = MONGODB_URL_KEY
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.database = MongoDBClient.client[database_name]
            self.database_name = database_name
            logging.info(f"MongoDB connection successful to the database: {self.database_name}")
        except Exception as e:
            raise USvisaException(e, sys) from e