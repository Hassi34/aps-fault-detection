
import argparse
import shutil
from src.utils.logging import logger
from src.utils.common import read_yaml
import pandas as pd
from src.utils.ml import TargetValueMapping
import shutil
from src.cloud_sync import CloudSync
from utils.ml import is_blessed
from utils.mlflow import MLFlowManager

STAGE = "Model Blessing"  # <<< change stage name

cloud_sync = CloudSync()
cloud_sync.download_logs()
# cloud_sync.upload_preblessing_test_report()
cloud_sync.download_trained_model()
cloud_sync.download_blessed_model()
cloud_sync.sync_gcs_to_local_data_dir()


def model_blessing(config_path, params_path):
    # read config files
    config = read_yaml(config_path)
    params = read_yaml(params_path)
    mlflow = MLFlowManager()
    monitoring_threshold = params['model_monitoring']['COST_THRESHOLD']
    model_name = config['mlflow']['MODEL_NAME']
    test_data_file_path = config['local_data']['TEST_PATH']

    trained_model_file_path = config['artifacts']['TRAINED_MODEL_FILE_PATH']
    blessed_model_file_path = config['artifacts']['BLESSED_MODEL_FILE_PATH']

    target = [config['base']['TARGET_COL']]
    test_df = pd.read_csv(test_data_file_path, sep=",", encoding='utf-8')

    test_y = test_df[target]
    test_y = test_y.replace(
        TargetValueMapping().to_dict()
    )
    test_X = test_df.drop(target, axis=1)

    proceed_blessing = is_blessed(test_X, test_y, monitoring_threshold,
                                  trained_model_file_path, blessed_model_file_path, logger)

    if not proceed_blessing:
        logger.info(
            "Current model is not better than the production model, terminating the pipeline...")
        cloud_sync.upload_logs()
        #raise Exception("Current model is not better than the production model, terminating the pipeline")
        # sys.exit(0)

    logger.info("All validations passed, Model has been blessed")
    shutil.copy(trained_model_file_path, blessed_model_file_path)
    logger.info(f"blessed model is available at {blessed_model_file_path}")

    latest_model_version = mlflow.latest_model_version(model_name=model_name)
    mlflow.transition_model_version_stage(
        model_name=model_name, model_version=latest_model_version, stage="Production")
    logger.info(
        f"Model latest version {latest_model_version} has been transitioned to MLFlow Production")

    cloud_sync.upload_blessed_model()
    logger.info("Uploaded the blessed model to Cloud Storage")


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        model_blessing(config_path=parsed_args.config,
                       params_path=parsed_args.params)
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
    except Exception as e:
        logger.exception(e)
        cloud_sync.upload_logs()
        raise e
    cloud_sync.upload_logs()
