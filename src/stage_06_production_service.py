
import argparse
import shutil
from src.utils.logging import logger
from src.utils.common import read_yaml
import pandas as pd
from src.utils.ml import TargetValueMapping
import joblib
import shutil
from src.cloud_sync import CloudSync
import shutil
import joblib

STAGE = "Production Serving"  # <<< change stage name
'''Model will be downloaded at this stage and will be copied to the production environment with shell script'''
cloud_sync = CloudSync()
cloud_sync.download_logs()


def serving(config_path):
    config = read_yaml(config_path)

    production_model_path = config['model_serving']['PRODUCTION_MODEL_PATH']
    blessed_model_path = config['artifacts']['BLESSED_MODEL_FILE_PATH']
    target_col_name = config['base']['TARGET_COL']
    cloud_sync.download_blessed_model()
    logger.info(f"Downloaded the blessed model to {blessed_model_path}")
    shutil.copy(blessed_model_path, production_model_path)
    logger.info(f"Blessed model copied to {production_model_path}")

    local_inputs_file_path = config['model_serving']['LOCAL_INPUTS_FILE_PATH']
    local_prediction_file_path = config['model_serving']['LOCAL_PREDICTION_FILE_PATH']

    cloud_sync.download_input_features()
    inputs = pd.read_csv(local_inputs_file_path, encoding='utf8', sep=",")
    logger.info(f"Inputs dataframe with the shape : {inputs.shape}")
    pipeline = joblib.load(production_model_path)
    y = pipeline.predict(inputs)
    inputs[target_col_name] = y
    inputs[target_col_name] = inputs[target_col_name].replace(
        TargetValueMapping().reverse_mapping()
    )
    inputs.to_csv(local_prediction_file_path,
                  encoding='utf8', sep=",", index=False)
    logger.info(
        f"Predictions have been saved at: {local_prediction_file_path}, having the shape: {inputs.shape}")
    cloud_sync.upload_predictions()


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    parsed_args = args.parse_args()

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        serving(config_path=parsed_args.config)
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
    except Exception as e:
        cloud_sync.upload_logs()
        logger.exception(e)
        raise e
    cloud_sync.upload_logs()
