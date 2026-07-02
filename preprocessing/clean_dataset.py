"""
Module: Data Cleaning
Removes duplicate and missing values.
"""


def clean_dataset(dataset):

    if dataset is None:

        return None

    print("\nCleaning Dataset...")

    dataset = dataset.drop_duplicates()

    dataset = dataset.dropna()

    print("Cleaning completed.")

    return dataset