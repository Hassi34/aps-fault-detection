from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, confusion_matrix
from .exceptions import NotInRange
import joblib 
import numpy as np
import pandas as pd

class TargetValueMapping:
    def __init__(self):
        self.neg: int = 0

        self.pos: int = 1

    def to_dict(self):
        return self.__dict__

    def reverse_mapping(self):
        mapping_response = self.to_dict()

        return dict(zip(mapping_response.values(), mapping_response.keys()))

def eval_metrics(actual, pred):
    accuracy = round(accuracy_score(actual, pred), 3)
    precision = round(precision_score(actual, pred), 3)
    recall = round(recall_score(actual, pred), 3)
    f1 = round(f1_score(actual, pred), 3)
    tn, fp, fn, tp = confusion_matrix(actual, pred).ravel()
    cost = round((10*fp + 500*fn), 3)
    return (accuracy, precision, recall, f1, cost)

def is_blessed(test_X : pd.DataFrame, test_y: pd.Series, monitoring_threshold: float,
               trained_model_path: str, production_model_path:str, logger: object) -> bool:
    trained_model = joblib.load(trained_model_path)
    production_model = joblib.load(production_model_path)
    trained_predictions = trained_model.predict(test_X)
    production_prediction =  production_model.predict(test_X)
    _, _, _, _, cost_trained = eval_metrics(test_y, trained_predictions)
    _, _, _, _, cost_production = eval_metrics(test_y, production_prediction)
    logger.info(f"Total cost with trained model: {cost_trained}, Total cost with production model: {cost_production}")
    if  cost_production - cost_trained >= monitoring_threshold:
        return True
    else: 
        return False

def predict(data_dict : dict, model_path: str , min_allowed: int, max_allowed: int):
    model = joblib.load(model_path)
    data = data_dict.values()
    #data = np.array([list(map(float, data))])
    data = pd.DataFrame.from_dict(data_dict, orient='index').T #to get the input values as pandas df
    prediction = model.predict(data)

    if min_allowed <= prediction <= max_allowed:
        return {'response': prediction}
    else:
        message = f"Prediction {prediction} is out of expected range: Max Allowed :{max_allowed} Min Allowed :{min_allowed}"
        raise NotInRange(message)
    