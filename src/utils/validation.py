
from .common import read_json, write_yaml
from .exceptions import NotInCols, NotInRange
import pandas as pd
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
import json

def validate_data(dict_request : dict, schema_file_path: str):
    schema = read_json(schema_file_path)
    actual_cols = schema.keys()
    def _validate_cols(col):
        if col not in actual_cols:
            message = f'Key "{col}" is not an expected key name. Expected keys:\n{actual_cols}' 
            raise NotInCols(message)
    
    for col, val in dict_request.items():
        _validate_cols(col)

    return True

def detect_data_drift(
        reference_df: pd.DataFrame, current_df: pd.DataFrame,
        data_drift_report_path: str, logger
    ) -> bool:
        """
        :param reference_df: base dataframe
        :param current_df: current dataframe
        :return: True if drift detected else False
        """
        data_drift_profile = Profile(sections=[DataDriftProfileSection()])

        data_drift_profile.calculate(reference_df, current_df)

        report = data_drift_profile.json()

        json_report = json.loads(report)

        write_yaml(
            file_path = data_drift_report_path,
            content = json_report,
        )

        n_features = json_report["data_drift"]["data"]["metrics"]["n_features"]

        n_drifted_features = json_report["data_drift"]["data"]["metrics"][
            "n_drifted_features"
        ]

        logger.info(f"{n_drifted_features}/{n_features} drift detected.")

        drift_status = json_report["data_drift"]["data"]["metrics"]["dataset_drift"]

        return drift_status