"""
Module: Load Dataset
Description: Loads a CSV dataset into a pandas DataFrame.
"""

import pandas as pd


def load_dataset(file_path):
    """
    Load a dataset from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pandas.DataFrame or None:
            Returns the dataset if loaded successfully,
            otherwise returns None.
    """
    try:
        data = pd.read_csv(file_path)

        print("\nDataset loaded successfully.")
        print("Rows    :", data.shape[0])
        print("Columns :", data.shape[1])

        return data

    except FileNotFoundError:
        print("Error: Dataset file not found.")
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None