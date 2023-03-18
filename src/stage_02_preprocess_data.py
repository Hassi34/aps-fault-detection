import argparse
from src.utils.common import read_yaml
import pandas as pd
from src.cloud_sync import CloudSync
from src.utils.logging import logger

STAGE = "Data Preprocessing"  # <<< change stage name

cloud_sync = CloudSync()
cloud_sync.download_logs()


def preprocess_data(config_path, params_path):
    # read config files
    config = read_yaml(config_path)
    params = read_yaml(params_path)

    train_data_file_path = config['local_data']['TRAIN_PATH']
    test_data_file_path = config['local_data']['TEST_PATH']
    raw_data_file_path = config['local_data']['RAW_DATA_FILE_PATH']

    train_data_size = params['split_data']['TRAIN_SIZE']
    random_state = params['base']['RANDOM_STATE']

    df = pd.read_csv(raw_data_file_path, sep=",", encoding='utf-8')
    logger.info(
        f"Loaded the raw data from {raw_data_file_path} have the shape {df.shape}")
    df.columns = [col.replace(" ", "_") for col in df.columns]
    train_df = df.sample(frac=train_data_size, random_state=random_state)
    test_df = df.drop(train_df.index)

    train_df.to_csv(train_data_file_path, sep=',', index=False)
    logger.info(
        f"Training data saved at {train_data_file_path} having the shape {train_df.shape}")
    test_df.to_csv(test_data_file_path, sep=',', index=False)
    logger.info(
        f"Test data saved at {test_data_file_path} having the shape {test_df.shape}")


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        preprocess_data(config_path=parsed_args.config,
                        params_path=parsed_args.params)
        cloud_sync.sync_local_data_dir_to_gcs()
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
    except Exception as e:
        logger.exception(e)
        cloud_sync.upload_logs()
        raise e
    cloud_sync.upload_logs()
