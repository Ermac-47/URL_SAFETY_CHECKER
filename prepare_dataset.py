import pandas as pd
import os

RAW_PATH = "data/raw/new_data_urls.csv"
BACKUP_PATH = "data/urls_original_backup.csv"
OUTPUT_PATH = "data/urls.csv"

ROWS_PER_CLASS = 200
RANDOM_SEED = 42


def main():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(
            "Could not find " + RAW_PATH + ". Did you run the kaggle download step?"
        )

    df = pd.read_csv(RAW_PATH)

    expected_cols = {"url", "status"}
    if not expected_cols.issubset(df.columns):
        raise ValueError("Expected columns " + str(expected_cols) + ", got " + str(list(df.columns)))

    df["label"] = 1 - df["status"]

    df = df.dropna(subset=["url"])
    df["url"] = df["url"].astype(str).str.strip()
    df = df[df["url"] != ""]

    phishing = df[df["label"] == 1]
    safe = df[df["label"] == 0]

    print("Source dataset: " + str(len(phishing)) + " phishing rows, " + str(len(safe)) + " safe rows available")

    if len(phishing) < ROWS_PER_CLASS or len(safe) < ROWS_PER_CLASS:
        raise ValueError("Not enough rows to sample " + str(ROWS_PER_CLASS) + " per class.")

    phishing_sample = phishing.sample(n=ROWS_PER_CLASS, random_state=RANDOM_SEED)
    safe_sample = safe.sample(n=ROWS_PER_CLASS, random_state=RANDOM_SEED)

    final = pd.concat([phishing_sample, safe_sample])[["url", "label"]]
    final = final.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    final["url"] = final["url"].apply(
        lambda u: u if u.startswith("http://") or u.startswith("https://") else "http://" + u
    )

    if os.path.exists(OUTPUT_PATH) and not os.path.exists(BACKUP_PATH):
        os.rename(OUTPUT_PATH, BACKUP_PATH)
        print("Backed up original " + OUTPUT_PATH + " -> " + BACKUP_PATH)

    final.to_csv(OUTPUT_PATH, index=False)
    print("Wrote " + str(len(final)) + " rows to " + OUTPUT_PATH)
    print(final["label"].value_counts())


if __name__ == "__main__":
    main()