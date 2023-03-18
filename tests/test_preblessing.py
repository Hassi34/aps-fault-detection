import argparse
import os
import shutil
from tqdm import tqdm
from src.utils.logging import logger
from src.utils.common import read_yaml, create_directories
import random
import pandas as pd
import numpy as np
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
from src.cloud_sync import CloudSync

STAGE = "Pre-blessing Tests" ## <<< change stage name

cloud_sync = CloudSync()
cloud_sync.download_logs()
cloud_sync.download_trained_model()
cloud_sync.download_preblessing_test_report()

logger.info(f'>>>>> stage "{STAGE}" started <<<<<')

config = read_yaml("configs/config.yaml")
params = read_yaml("params.yaml")

test_data_file_path = config['local_data']['TEST_PATH']

trained_model_file_path = config['artifacts']['TRAINED_MODEL_FILE_PATH']
prediction_schema_dir = config['artifacts']['PREDICTION_SCHEMA_DIR']

min_expected_pred_value = params['prediction']['MIN_EXPECTED_PRED_VALUE']
max_expected_pred_value = params['prediction']['MAX_EXPECTED_PRED_VALUE']

prediction_schema_file_path = os.path.join(prediction_schema_dir, config['artifacts']['PREDICTION_SCHEMA_FILE_NAME'])

input_data = {

    "incorrect_col":{
    "aa 000": 23,
    "ab 921000": 0.0
    }
}

def test_data_validation_exception_for_incorrect_col(data=input_data["incorrect_col"]):
    with pytest.raises(NotInCols):
        res = validate_data(data, prediction_schema_file_path)

logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
cloud_sync.upload_preblessing_test_report()
cloud_sync.upload_logs()