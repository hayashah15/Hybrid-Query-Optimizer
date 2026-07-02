"""
Module: Dataset Summary
Description: Displays useful information about the dataset.
"""


def dataset_summary(data):
    """
    Display basic information about the dataset.

    Parameters:
        data (pandas.DataFrame): The dataset to summarize.
    """
    if data is None:
        print("Dataset not available.")
        return

    print("\nDataset Information")
    print("-" * 50)

    data.info()

    print("\nFirst Five Records\n")
    print(data.head())