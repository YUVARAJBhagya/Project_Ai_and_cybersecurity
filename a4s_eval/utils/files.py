import os

import pandas as pd
from a4s_eval.utils import env
import requests

DATASET_DIR = "datasets"
MODEL_DIR = "models"


def download_file(url: str, path: str) -> None:
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Check for errors
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)


def get_dataset_files(dataset_file: str) -> str:
    cache_dir = f"{env.CACHE_DIR}/{DATASET_DIR}"
    os.makedirs(cache_dir, exist_ok=True)

    url = f"{env.API_URL}/api/dataset_file?file_name={dataset_file}"
    file_path = f"{cache_dir}/{dataset_file}"
    if not os.path.exists(file_path):
        download_file(url, file_path)
    return file_path


def get_model_files(model_file: str) -> str:
    cache_dir = f"{env.CACHE_DIR}/{MODEL_DIR}"
    os.makedirs(cache_dir, exist_ok=True)

    url = f"{env.API_URL}/api/model_file?file_name={model_file}"
    file_path = f"{cache_dir}/{model_file}"
    if not os.path.exists(file_path):
        download_file(url, file_path)
    return file_path


def auto_read_dataset_file(dataset_file: str) -> pd.DataFrame:
    if dataset_file.endswith(".csv"):
        return pd.read_csv(dataset_file)
    elif dataset_file.endswith(".parquet"):
        return pd.read_parquet(dataset_file)
    else:
        raise ValueError(f"Unsupported file format: {dataset_file}")


def auto_get_read_dataset_file(dataset_file: str) -> pd.DataFrame:
    file_path = get_dataset_files(dataset_file)
    return auto_read_dataset_file(file_path)
