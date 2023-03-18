
import argparse
from src.utils.logging import logger
from src.cloud_sync import CloudSync

STAGE = "Pre-production Setup"  # <<< change stage name
'''Model will be downloaded at this stage and will be copied to the production environment with shell script'''
cloud_sync = CloudSync()
cloud_sync.download_logs()


def preprod_setup():
    cloud_sync.download_blessed_model()
    logger.info("Downloaded the blessed model from the Cloud Storage")


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        preprod_setup()
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
    except Exception as e:
        cloud_sync.upload_logs()
        logger.exception(e)
        raise e
    cloud_sync.upload_logs()
