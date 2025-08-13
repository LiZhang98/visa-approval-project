import os
import sys

from pandas import DataFrame
from sklearn.model_selection import train_test_split

from visa_approval.exception import USvisaException
from visa_approval.logger import logging
from visa_approval.entity.artifact_entity import DataIngestionArtifact
from visa_approval.entity.config_entity import DataIngestionConfig
from visa_approval.data_access.visa_data import VisaData

class DataIngestion:
    
    def __init__(self, data_ingestion_config: DataIngestionConfig = DataIngestionConfig()):
        
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise USvisaException(e, sys)
            

    def export_data_into_feature_store(self) -> DataFrame:
        
        try:
            logging.info("Exporting data from mongodb")
            visa_data = VisaData()
            data_frame = visa_data.export_collection_as_dataframe(
                collection_name=self.data_ingestion_config.collection_name
            )
            logging.info(f"Shape of data frame: {data_frame.shape}")
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Saving data frame to {feature_store_file_path}")
            data_frame.to_csv(feature_store_file_path, index=False, header=True)
            return data_frame
        except Exception as e:
            raise USvisaException(e, sys)
        
        
    
    def split_data_as_train_test(self, data_frame: DataFrame) -> None:
        
        logging.info("Splitting data into train and test sets")
        
        try:
            train_set, test_set = train_test_split(
                data_frame,
                test_size=self.data_ingestion_config.train_test_split_ratio   
            )
            
            logging.info("Performed train test split")
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False,
                header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False,
                header=True
            )
            
            logging.info("Exported train and test file path")
            
        except Exception as e:
            raise USvisaException(e, sys)
        
        
    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        
        try:
            data_fram = self.export_data_into_feature_store()
            
            logging.info("Got the data from mongodb")
            
            self.split_data_as_train_test(data_frame=data_fram)
            
            logging.info("Performed train test split on the dataset")
            
            data_ingestion_artifact = DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                            test_file_path=self.data_ingestion_config.testing_file_path)
            
            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        
        except Exception as e:
            raise USvisaException(e, sys)