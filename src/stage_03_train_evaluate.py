import argparse
import os
from src.utils.common import read_yaml, create_directories
from src.utils.ml import eval_metrics
import joblib
import json
import mlflow
import pandas as pd
import numpy as np
from src.utils.ml import TargetValueMapping
from utils import MLFlowManager
from datetime import datetime
from mlflow.sklearn import log_model
from mlflow.models.signature import infer_signature
from src.cloud_sync import CloudSync
from src.utils.logging import logger
from pycaret.classification import *

STAGE = "Training and Evaluation"  # <<< change stage name

cloud_sync = CloudSync()
cloud_sync.download_logs()


def train_evalute(config_path, params_path):
    # read config files
    config = read_yaml(config_path)
    params = read_yaml(params_path)

    train_data_file_path = config['local_data']['TRAIN_PATH']
    test_data_file_path = config['local_data']['TEST_PATH']
    raw_data_file_path = config['local_data']['RAW_DATA_FILE_PATH']
    target_col_name = config['base']['TARGET_COL']
    #artifact_dir = config['artifacts']['ARTIFACTS_DIR']
    trained_model_dir = config['artifacts']['TRAINED_MODEL_DIR']
    #model_dir = os.path.join(artifact_dir, model_dir)
    reports_dir = config['artifacts']['REPORTS_DIR']
    prediction_schema_dir = config['artifacts']['PREDICTION_SCHEMA_DIR']
    create_directories([trained_model_dir, reports_dir, prediction_schema_dir])
    model_score_report_path = config['artifacts']['MODEL_EVAL_REPORT_PATH']
    training_param_report_path = config['artifacts']['TRAINING_PARAMS_REPORT_PATH']

    prediction_schema_file_path = os.path.join(
        prediction_schema_dir, config['artifacts']['PREDICTION_SCHEMA_FILE_NAME'])

    target = [config['base']['TARGET_COL']]
    mlflow_service = MLFlowManager()
    experiment_name = config['mlflow']['EXPERIMENT_NAME']
    experiment_id = mlflow_service.get_or_create_an_experiment(experiment_name)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    run_name = config['mlflow']['RUN_ID_PREFIX'] + "-" + timestamp

    mlflow_model_name = config['mlflow']['MODEL_NAME']
    logged_model_dir = config['mlflow']['LOGGED_MODEL_DIR']

    train_df = pd.read_csv(train_data_file_path, sep=",", encoding='utf-8')
    test_df = pd.read_csv(test_data_file_path, sep=",", encoding='utf-8')
    raw_df = pd.read_csv(raw_data_file_path, sep=",", encoding='utf-8')

    train_y = train_df[target]
    train_y = train_y.replace(
        TargetValueMapping().to_dict()
    )
    test_y = test_df[target]
    test_y = test_y.replace(
        TargetValueMapping().to_dict()
    )

    train_X = train_df.drop(target, axis=1)
    test_X = test_df.drop(target, axis=1)
    logger.info(
        f"train_X shape: {train_X.shape}, test_X shape :{test_X.shape}")
    X_df = pd.concat([train_X, test_X])
    logger.info(f"X_df shape: {X_df.shape}")
    train_processed_complete_data = pd.concat([train_X, train_y], axis=1)
    summary = X_df.describe()
    summary.loc[['min', 'max']].to_json(prediction_schema_file_path)
    logger.info(f"Wrote the data schema to : {prediction_schema_file_path}")
    cloud_sync.upload_prediction_schema()
    logger.info("Uploaded the schema to cloud")

    logger.info("AutoML experiment started...")
    exp = ClassificationExperiment()
    exp.setup(train_processed_complete_data,
              target=target_col_name,
              use_gpu=False,
              train_size=0.7,
              numeric_imputation='knn',
              categorical_imputation='mode',
              fix_imbalance=True,
              fix_imbalance_method="smote",
              preprocess=True,
              low_variance_threshold=0.0)
    best_model = exp.compare_models(n_select=1, sort='F1')
    # tuned_top3 = [exp.tune_model(i) for i in top3]
    # blender = exp.blend_models(tuned_top3)
    # stacker = exp.stack_models(tuned_top3)
    # best_model = exp.automl(optimize = 'F1')

    params = {}
    model_params = (dict(best_model.get_params()))
    for param in model_params:
        params[str(param)] = str(model_params[param])

    pipeline = exp.finalize_model(best_model)
    logger.info("Created the prediction pipeline with the best model")

    mlflow.sklearn.autolog()
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name):
        logger.info(
            f'Model training started with experiment name : "{experiment_name}" and run name :"{run_name}"')
        pipeline.fit(train_X, train_y)
        logger.info("Model training completed!")
        y_hat = pipeline.predict(test_X)
        accuracy, precision, recall, f1, cost = eval_metrics(test_y, y_hat)
        mlflow.log_metrics({
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'cost': cost
        })

        logger.info(
            f"Experiment logging completed with Parameter :\n {params}")
        logger.info(f"Training params saved at : {training_param_report_path}")
        logger.info(
            f"Model Eval result : accuracy: {accuracy} precision: {precision} recall: {recall} f1_score : {recall} cost : {cost}")
        print(
            f"Model Eval result : accuracy: {accuracy} precision: {precision} recall: {recall} f1_score : {recall} cost : {cost}")
        model_path = os.path.join(trained_model_dir, "model.joblib")
        joblib.dump(pipeline, model_path)
        logger.info(f"Trained model saved at : {model_path}")
        cloud_sync.upload_trained_model()
        logger.info("Uploaded the trained model to cloud storage")

        signature = infer_signature(train_X, pipeline.predict(train_X))
        log_model(pipeline,
                  artifact_path=logged_model_dir,
                  registered_model_name=mlflow_model_name,
                  signature=signature)
    def convert(o):
        if isinstance(o, np.generic): return o.item()  
        raise TypeError
    with open(model_score_report_path, 'w') as f:
        scores = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'cost': np.int64(cost),
        }
        json.dump(scores, f, indent=4, default=convert)
    logger.info(f"Model Scores saved at : {model_score_report_path}")

    with open(training_param_report_path, 'w') as f:
        json.dump(params, f, indent=4)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", "-c", default="configs/config.yaml")
    args.add_argument("--params", "-p", default="params.yaml")
    parsed_args = args.parse_args()

    try:
        logger.info("\n********************")
        logger.info(f'>>>>> stage "{STAGE}" started <<<<<')
        train_evalute(config_path=parsed_args.config,
                      params_path=parsed_args.params)
        logger.info(f'>>>>> stage "{STAGE}" completed!<<<<<\n')
    except Exception as e:
        cloud_sync.upload_logs()
        logger.exception(e)
        raise e
    cloud_sync.upload_logs()
