"""
Prepare data: convert metadata.jsonl to CSV format and split into train/val sets.
"""
import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split

IMAGE_DIR = "image_resource"
METADATA_FILE = "metadata.jsonl"
OUTPUT_DIR = "data"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    records = []
    with open(METADATA_FILE, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            # image filename: "test/dish_xxx.png" -> "dish_xxx.png"
            image_filename = os.path.basename(entry["file_name"])
            image_path = os.path.join(IMAGE_DIR, image_filename)

            # Skip if image doesn't exist
            if not os.path.exists(image_path):
                continue

            records.append({
                "image": image_filename,
                "total_calories": entry["total_calories"],
                "total_fat": entry["total_fat"],
                "total_carb": entry["total_carb"],
                "total_protein": entry["total_protein"],
                "total_mass": entry["total_mass"],
            })

    df = pd.DataFrame(records)
    print(f"Total valid samples: {len(df)}")
    print(f"\nTarget statistics:")
    print(df[["total_calories", "total_fat", "total_carb", "total_protein"]].describe())

    # Split: 80% train, 20% validation
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    print(f"\nTrain samples: {len(train_df)}")
    print(f"Val samples: {len(val_df)}")

    train_df.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(OUTPUT_DIR, "val.csv"), index=False)
    print(f"\nSaved to {OUTPUT_DIR}/train.csv and {OUTPUT_DIR}/val.csv")


if __name__ == "__main__":
    main()
