"""
Module: Dataset Summary
Displays useful information about the dataset.
"""


def dataset_summary(dataset):

    if dataset is None:

        print("Dataset not available.")

        return

    print("\nDataset Information")
    print("-" * 40)

    dataset.info()

    print("\nFirst Five Records")
    print(dataset.head())