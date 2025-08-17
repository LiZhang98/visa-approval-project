import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder, PowerTransformer
from sklearn.compose import ColumnTransformer
from pandas import DataFrame

from visa_approval.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR
from visa_approval.entity.config_entity import DataTransformationConfig
from visa_approval.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact
from visa_approval.exception import USvisaException
from visa_approval.logger import logging
from visa_approval.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file, drop_columns
from visa_approval.entity.estimator import TargetValueMapping

class DataTransformation:
    
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            
        except Exception as e:
            raise USvisaException(e, sys)
    
    
    @staticmethod
    def read_data(file_path) -> DataFrame:
        
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise USvisaException(e, sys)
        
    
    def get_data_transformation_object(self) -> Pipeline:
        
        logging.info("Enterted the get_data_tranformation_object method of DataTransformation class")
        
        
        try:
            
            numeric_transformer = StandardScaler()
            oh_transformer = OneHotEncoder()
            ordinal_encoder = OrdinalEncoder()
            
            logging.info("Initialized numerical, categorical and ordinal transformers")
            
            oh_columns = self._schema_config["oh_columns"]
            or_columns = self._schema_config["or_columns"]
            transform_columns = self._schema_config["transform_columns"]
            num_features = self._schema_config["num_features"]
            
            logging.info(f"Initialize PowerTransformer")
            
            transform_pipe = Pipeline(steps=[('transformer', PowerTransformer(method='yeo-johnson'))])
            
            preprocessor = ColumnTransformer(
                [
                   ("OneHotEncoder", oh_transformer, oh_columns),
                   ("Ordinal_Encoder", ordinal_encoder, or_columns),
                   ("Tranformer", transform_pipe, transform_columns),
                   ("StandardScaler", numeric_transformer, num_features)
                    
                ]
            )
            
            logging.info("Created preprocessor object from ColumnTransformer")
            logging.info("Exited the get_data_transformation_object method of DataTransformation class")
            return preprocessor
        
        except Exception as e:
            raise USvisaException(e, sys)
        
    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        
        try:
            if self.data_validation_artifact.validation_status:
                logging.info("Starting data transformation:")
                preprocessor = self.get_data_transformation_object()
                logging.info("Got the preprocessor object")
                
                train_df =  DataTransformation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
                test_df = DataTransformation.read_data(file_path=self.data_ingestion_artifact.test_file_path)
                
                input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
                target_feature_train_df = train_df[TARGET_COLUMN]
                
                input_feature_train_df['company_age'] = CURRENT_YEAR - input_feature_train_df['yr_of_estab']
                logging.info("Added company_age feature to the training data")
                
                drop_cols = self._schema_config['drop_columns']
                input_feature_train_df = drop_columns(df=input_feature_train_df, cols=drop_cols)
                logging.info("Dropped unnecessary columns from the training data")
                
                target_feature_train_df = target_feature_train_df.replace(TargetValueMapping()._asdict())
                
                input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
                target_feature_test_df = test_df[TARGET_COLUMN]
                
                input_feature_test_df['company_age'] = CURRENT_YEAR - input_feature_test_df['yr_of_estab']
                logging.info("Added company_age feature to the test data")
                
                input_feature_test_df = drop_columns(df=input_feature_test_df, cols=drop_cols)
                logging.info("Dropped unnecessary columns from the test data")
                
                target_feature_test_df = target_feature_test_df.replace(TargetValueMapping()._asdict())
                logging.info("Replaced target values in the test data")
                
                logging.info("Got train and test features of Testing dataset")
                logging.info("Applying preprocessing object on training dataframe and testing dataframe")
                
                input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)
                input_feature_test_arr = preprocessor.transform(input_feature_test_df)
                logging.info("Applied preprocessing object on training and testing dataframes")
                
                logging.info("Applying SMOTEENN on training data")
                
                smt = SMOTEENN(sampling_strategy="minority")
                
                input_feature_train_final, target_feature_train_final = smt.fit_resample(input_feature_train_arr, target_feature_train_df)
                logging.info("Applied SMOTEENN on training data")
                
                logging.info("Appying SMOTEENN on testing data")
                input_feature_test_final, target_feature_test_final = smt.fit_resample(input_feature_test_arr, target_feature_test_df)
                logging.info("Applied SMOTEENN on testing data")
                
                train_arr = np.c_[input_feature_train_final, np.array(target_feature_train_final)]
                test_arr = np.c_[input_feature_test_final, np.array(target_feature_test_final)]
                
                save_object(self.data_transformation_config.transformed_object_file_path, preprocessor)
                save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
                save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
                
                logging.info("Saved preprocessor, transformed train and test data to respective file paths")
                
                logging.info("Exited the initiate_data_transformation method of DataTransformation class")
                
                data_transformation_artifact = DataTransformationArtifact(
                    transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                    transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                    transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
                )
                
                return data_transformation_artifact
            else:
                raise Exception(self.data_validation_artifact.message)
        
        except Exception as e:
            raise USvisaException(e, sys)