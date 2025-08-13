import os 
from datetime import date

DATABASE_NAME = "EasyVisa"

COLLECTION_NAME = "visa_data"

MONGODB_URL_KEY = "mongodb+srv://317403125z:317403125z@cluster0.gcf1aec.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

PIPELINE_NAME: str = "visa_approval"
ARTIFACT_DIR: str = "artifact"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

FILE_NAME: str = "visa_approval.csv"
MODEL_FILE_NAME = "model.pkl"


'''
Data ingestion related constants start with DATA_INGESTION VAR NAME
'''

DATA_INGESTION_COLLECTION_NAME: str = "visa_data"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2

