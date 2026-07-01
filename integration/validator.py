import os

folders = [
    "backend",
    "database",
    "preprocessing",
    "integration",
    "docs",
    "tests",
    "results",
    "data"
]

def validate_project():

    print("Checking Project Structure...\n")

    for folder in folders:

        if os.path.exists(folder):
            print(f"✔ {folder} exists")

        else:
            print(f"✘ {folder} missing")


if __name__ == "__main__":
    validate_project()