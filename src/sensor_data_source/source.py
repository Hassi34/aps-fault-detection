
from typing import Optional
import os

import numpy as np
import pandas as pd

from src.utils import MongoDBClient

from dotenv import load_dotenv
load_dotenv()

MONGO_DATABASE_NAME = os.environ['MONGO_DATABASE_NAME']

class SensorData:
    """
    This class help to export entire mongo db record as pandas dataframe
    """

    def __init__(self):
        self.mongo_client = MongoDBClient(database_name=MONGO_DATABASE_NAME)

    def export_collection_as_dataframe(
        self, collection_name: str, database_name: Optional[str] = None) -> pd.DataFrame:
        """
        export entire collectin as dataframe:
        return pd.DataFrame of collection
        """
        if database_name is None:
            collection = self.mongo_client.database[collection_name]

        else:
            collection = self.mongo_client[database_name][collection_name]

        df = pd.DataFrame(list(collection.find().limit(400)))

        if "_id" in df.columns.to_list():
            df = df.drop(columns=["_id"], axis=1)

        df.replace({"na": np.nan}, inplace=True)

        return df