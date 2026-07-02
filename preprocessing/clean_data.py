"""
Module: Data Cleaning
Description: Performs basic cleaning on the dataset.
"""


def clean_dataset(data):
    """
    Perform basic data cleaning.

    Removes duplicate rows and rows with missing values.

    Parameters:
        data (pandas.DataFrame): The dataset to clean.

    Returns:
        pandas.DataFrame or None:
            The cleaned dataset, or None if no dataset is provided.
    """
    if data is None:
        return None

    print("\nCleaning Dataset...")

    cleaned_data = data.drop_duplicates()
    cleaned_data = cleaned_data.dropna()

    print("Cleaning completed.")

    return cleaned_data