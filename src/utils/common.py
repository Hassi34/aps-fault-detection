import os
import yaml
import time
import pandas as pd
import json

def read_yaml(path_to_yaml: str) -> dict:
    with open(path_to_yaml) as yaml_file:
        content = yaml.safe_load(yaml_file)
    return content

def write_yaml(file_path: str, content: object, replace: bool = False) -> None:
    if replace:
        if os.path.exists(file_path):
            os.remove(file_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as file:
        yaml.dump(content, file)

def create_directories(path_to_directories: list) -> None:
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)


def save_json(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def read_json(path: str) -> dict:
    with open(path, "r") as json_file:
        content = json.load(json_file)
    return content