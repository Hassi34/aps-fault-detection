import argparse
from src.utils.logging import logger
from src.utils.common import read_yaml
from src.cloud_sync import CloudSync
from utils.validation import detect_data_drift
import pandas as pd
from src.sensor_data_source import SensorData


STAGE = "Load Data"  # <<< change stage name
cloud_sync = CloudSync()


def download_data(config_path, params_path):
    # read config files
    config = read_yaml(config_path)
    params = read_yaml(params_path)

    local_data = config['local_data']
    raw_data_file_path = local_data['RAW_DATA_FILE_PATH']

    check_data_drift = params['model_monitoring']['CHECK_DATA_DRIFT']
    data_drift_report_path = config['model_serving']['DATA_DRIFT_REPORT_PATH']

    # This will download the current data from gcs
    cloud_sync.sync_gcs_to_local_data_dir()
    reference_df = pd.read_csv(raw_data_file_path, sep=",", encoding='utf-8')

    mongo_collection_name = config['source_download']['MONGO_DB_COLLECTION_NAME']
    source_data = SensorData()
    raw_df = source_data.export_collection_as_dataframe(
        collection_name=mongo_collection_name)
    raw_df.to_csv(raw_data_file_path, encoding='utf8', index=False, sep=",")

    logger.info(
        f"Downloaded the data from MongoDB and saved at {raw_data_file_path}")
    current_df = pd.read_csv(raw_data_file_path, sep=",", encoding='utf-8')

    if check_data_drift:
        drift = detect_data_drift(
            reference_df, current_df, data_drift_report_path, logger)
        cloud_sync.upload_drift_report()
        logger.info("Drift report has been uploaded to GCS")
        if not drift:
            logger.info(
                "No data drift detected, terminating the experiment...")
            cloud_sync.upload_logs()
            raise Exception("No data drift detected, experiment terminated")
    else:
        logger.info(
            "'Check Data Drift' has been set to False, skipping data drift...")


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        download_data(config_path=parsed_args.config,
                      params_path=parsed_args.params)
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
    except Exception as e:
        logger.exception(e)
        cloud_sync.upload_logs()
        raise e
    cloud_sync.sync_local_data_dir_to_gcs()
    cloud_sync.upload_logs()
