import logging
import logging.handlers
from src.utils.common import read_yaml


config = read_yaml("configs/config.yaml")

LOGS_FILE_PATH = config['logs']['LOGS_FILE_PATH']

logger = logging.getLogger()
fh = logging.handlers.RotatingFileHandler(LOGS_FILE_PATH, maxBytes=10240, backupCount=5)
fh.setLevel(logging.DEBUG)#no matter what level I set here
formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(lineno)s] : %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
#logger.info('INFO')
#logger.error('ERROR')
logger.setLevel(logging.INFO)
