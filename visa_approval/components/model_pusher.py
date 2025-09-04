import sys

from visa_approval.cloud_storage.aws_storage import SimpleStorageService
from visa_approval.exception import USvisaException
from visa_approval.logger import logging
from visa_approval.entity.config_entity import ModelPusherConfig
from visa_approval.entity.artifact_entity import ModelPusherArtifact, ModelEvaluationArtifact
from visa_approval.entity.s3_estimator import VisaEstimator

class ModelPusher:
    
    def __init__(self, model_evaluation_artifact: ModelEvaluationArtifact,
                 model_pusher_config: ModelPusherConfig):
        
        self.s3 = SimpleStorageService()
        self.model_evaluation_artifact = model_evaluation_artifact
        self.model_pusher_config = model_pusher_config
        self.visa_estimator = VisaEstimator(
            bucket_name=model_pusher_config.bucket_name,
            model_path=model_pusher_config.s3_model_key_path
        )
        
        
    def initiate_model_pusher(self) -> ModelPusherArtifact:
        
        try:
            
            logging.info("Uploading artifacts folder to s3 bucket")
            self.visa_estimator.save_model(from_file=self.model_evaluation_artifact.trained_model_path)
            
            model_pusher_artifact = ModelPusherArtifact(bucket_name=self.model_pusher_config.bucket_name,
                                                        s3_model_path=self.model_pusher_config.s3_model_key_path)
            
            logging.info("Uploaded artifacts folder to s3 bucket")
            logging.info(f"Model pusher artifacgt: [{model_pusher_artifact}]")
            logging.info("Exited initiate_model_pusher method of ModelTrainer class")
            
            return model_pusher_artifact
        except Exception as e:
            raise USvisaException(e, sys)