import os
from src.config import *

def create_structure():

    dirs = [
        "model_serving",
        os.path.join("data","raw"),
        os.path.join("tests"),
        os.path.join("data","preprocessed"),
        os.path.join("artifacts", "trained_model"),
        os.path.join("artifacts", "blessed_model"),
        os.path.join("artifacts", "prediction_schema"),
        os.path.join("artifacts", "reports"),
        os.path.join("model_serving", "production_model"),
        os.path.join("model_serving", "data"),
        #os.path.join("model_serving", "utils"),
        #os.path.join("model_serving", "schemas"),
        #"notebooks",
        "logs",
        "src",
        os.path.join("src", "config")
    ]

    for dir_ in dirs:
        os.makedirs(dir_, exist_ok= True)
        with open(os.path.join(dir_, ".gitkeep"), "w") as f:
            pass 

    files = [
        "dvc.yaml",
        "params.yaml",
        ".gitignore",
        os.path.join("src", "__init__.py"),
        os.path.join("src", "config", "__init__.py"),
        os.path.join("model_serving", "__init__.py"),
        #os.path.join("model_serving","utils", "__init__.py"),
        #os.path.join("model_serving","requirements.txt"),
        os.path.join("logs", "running_logs.log")
    ]   

    for file in files:
        if not os.path.exists(file):
            with open(file, "w") as f:
                pass

if __name__ == "__main__":
    create_structure()