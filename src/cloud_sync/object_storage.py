import argparse
import os
import shutil
from tqdm import tqdm
import logging
from src.utils.common import read_yaml, create_directories
import random
import pandas as pd
import numpy as np
from src.utils.simple_storage_service import SimpleStorageService
from src.utils.ml import eval_metrics
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import joblib
import json
from src.utils.ml import predict
from src.utils.validation import validate_data
import shutil
from src.utils.exceptions import NotInCols, NotInRange
import pytest 
from src.utils.validation import validate_data
from src.utils.gcp_bucket import BucketGCP

STAGE = "Pre-blessing Tests" ## <<< change stage name 
logging.info(f'>>>>> stage "{STAGE}" started <<<<<')
logging.basicConfig(
    filename=os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(lineno)s] : %(message)s",
    filemode="a"
    )

config = read_yaml("configs/config.yaml")
params = read_yaml("params.yaml")

LOCAL_DATA_DIR = config['local_data']['DATA_DIR']

BUCKET_NAME = config['gs_config']['BUCKET_NAME']
GCS_DATA_DIR = config['gs_config']['DATA_DIR']

GS_TRAINED_MODEL = config['gs_config']['TRAINED_MODEL_PATH']
GS_BLESSED_MODEL = config['gs_config']['BLESSED_MODEL_PATH']
GS_PREDICTION_SCHEMA_PATH = config['gs_config']['PREDICTION_SCHEMA_PATH']
GS_PREBLESSING_REPORT_PATH = config['gs_config']['PREBLESSING_REPORT_PATH']
GS_LOGS_FILE_PATH = config['gs_config']['LOGS_FILE_PATH']
GS_DRIFT_REPORT_PATH = config['gs_config']['DATA_DRIFT_REPORT_PATH']

LOCAL_DATA_DRIFT_REPORT_PATH = config['model_serving']['DATA_DRIFT_REPORT_PATH']
TRAINED_MODEL_FILE_PATH = config['artifacts']['TRAINED_MODEL_FILE_PATH']
BLESSED_MODEL_FILE_PATH = config['artifacts']['BLESSED_MODEL_FILE_PATH']
PREDICTION_SCHEMA_FILE_PATH = config['artifacts']['PREDICTION_SCHEMA_FILE_PATH']
PRE_BLESSING_TEST_REPORT_PATH = config['artifacts']['PRE_BLESSING_TEST_REPORT_PATH']
LOGS_FILE_PATH = config['logs']['LOGS_FILE_PATH']

S3_REGION_NAME = config['model_serving']['S3_REGION_NAME']
S3_BUCKET_NAME = config['model_serving']['S3_BUCKET_NAME']
INPUT_DATA_S3_KEY = config['model_serving']['INPUT_DATA_S3_KEY']
PREDICTED_DATA_S3_KEY = config['model_serving']['PREDICTED_DATA_S3_KEY']
LOCAL_INPUTS_FILE_PATH = config['model_serving']['LOCAL_INPUTS_FILE_PATH']
LOCAL_PREDICTION_FILE_PATH = config['model_serving']['LOCAL_PREDICTION_FILE_PATH']  

class CloudSync:
    def __init__(self):
        self.gcs = BucketGCP(bucket_name = BUCKET_NAME)
        self.s3 = SimpleStorageService(region_name= S3_REGION_NAME,
                                       s3_bucket_name= S3_BUCKET_NAME)
        
    def sync_local_data_dir_to_gcs(self):
        cmd = f"gsutil -m cp -R {LOCAL_DATA_DIR} gs://{GCS_DATA_DIR}"

        os.system(cmd)

    def sync_gcs_to_local_data_dir(self):
        cmd = f"gsutil -m cp -R gs://{GCS_DATA_DIR}/data ./"
        os.system(cmd)

    def upload_drift_report(self):
        self.gcs.upload_file(LOCAL_DATA_DRIFT_REPORT_PATH, GS_DRIFT_REPORT_PATH)

    def upload_trained_model(self):
        self.gcs.upload_file(TRAINED_MODEL_FILE_PATH, GS_TRAINED_MODEL)

    def upload_blessed_model(self):
        self.gcs.upload_file(BLESSED_MODEL_FILE_PATH, GS_BLESSED_MODEL)

    def upload_prediction_schema(self):
        self.gcs.upload_file(PREDICTION_SCHEMA_FILE_PATH, GS_PREDICTION_SCHEMA_PATH)

    def upload_logs(self):
        self.gcs.upload_file(LOGS_FILE_PATH, GS_LOGS_FILE_PATH)

    def upload_preblessing_test_report(self):
        self.gcs.upload_file(PRE_BLESSING_TEST_REPORT_PATH, GS_PREBLESSING_REPORT_PATH)

    def download_trained_model(self):
        self.gcs.download_file(GS_TRAINED_MODEL, TRAINED_MODEL_FILE_PATH)

    def download_blessed_model(self):
        self.gcs.download_file(GS_BLESSED_MODEL, BLESSED_MODEL_FILE_PATH)

    def download_prediction_schema(self):
        self.gcs.download_file(GS_PREDICTION_SCHEMA_PATH, PREDICTION_SCHEMA_FILE_PATH)

    def download_preblessing_test_report(self):
        self.gcs.download_file(GS_PREBLESSING_REPORT_PATH, PRE_BLESSING_TEST_REPORT_PATH)

    def download_logs(self):
        self.gcs.download_file(GS_LOGS_FILE_PATH, LOGS_FILE_PATH)

    def download_input_features(self):
        self.s3.download_file(INPUT_DATA_S3_KEY, LOCAL_INPUTS_FILE_PATH)

    def upload_predictions(self):
        self.s3.upload_file(PREDICTED_DATA_S3_KEY, LOCAL_PREDICTION_FILE_PATH)
