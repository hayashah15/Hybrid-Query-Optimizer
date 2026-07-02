"""
Module: Load Dataset
Description:
Loads a CSV dataset into a pandas DataFrame.
"""

import pandas as pd


def load_dataset(file_path):
    """
    Load dataset from CSV file.
    """

    try:
        dataset = pd.read_csv(file_path)

        print("\nDataset loaded successfully.")
        print(f"Rows    : {dataset.shape[0]}")
        print(f"Columns : {dataset.shape[1]}")

        return dataset

    except FileNotFoundError:

        print("Dataset file not found.")

        return None

    except Exception as error:

        print("Error:", error)

        return None