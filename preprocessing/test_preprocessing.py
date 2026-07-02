from load_dataset import load_dataset
from dataset_summary import dataset_summary
from clean_dataset import clean_dataset


dataset = load_dataset("../data/raw/sample.csv")

dataset_summary(dataset)

dataset = clean_dataset(dataset)

print("\nPreprocessing completed successfully.")