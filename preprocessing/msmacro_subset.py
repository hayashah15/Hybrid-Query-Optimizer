import zipfile
import json
import csv
import io
import os

ZIP_PATH = "data/raw/msmarco.zip"
OUTPUT_CSV = "data/processed/msmarco_30k.csv"
TARGET_ROWS = 30000

os.makedirs("data/processed", exist_ok=True)

count = 0

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    names = z.namelist()
    print("Scanning zip contents...")

    corpus_name = None
    for name in names:
        if name.endswith("corpus.jsonl"):
            corpus_name = name
            break

    if corpus_name is None:
        raise FileNotFoundError("Could not find corpus.jsonl inside msmarco.zip")

    print(f"Using corpus file: {corpus_name}")

    with z.open(corpus_name, "r") as raw_file:
        text_file = io.TextIOWrapper(raw_file, encoding="utf-8")

        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(["text"])

            for line in text_file:
                line = line.strip()
                if not line:
                    continue

                obj = json.loads(line)
                text = obj.get("text", "").strip()

                if text:
                    writer.writerow([text])
                    count += 1

                if count % 5000 == 0 and count > 0:
                    print(f"Written {count} rows...")

                if count >= TARGET_ROWS:
                    break

print(f"\nDone. Wrote {count} rows to {OUTPUT_CSV}")
print(f"Output file size: {os.path.getsize(OUTPUT_CSV)} bytes")