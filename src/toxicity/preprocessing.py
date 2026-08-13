import re

import pandas as pd
from datasets import load_dataset


# ----------------------------------------
# Clean Text
# ----------------------------------------

def clean_text(text: str) -> str:
    """
    Clean text before training.
    """

    text = str(text).lower()

    text = re.sub(r"http\S+", "", text)

    text = re.sub(r"www\S+", "", text)

    text = re.sub(r"<.*?>", "", text)

    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


# ----------------------------------------
# Load & Preprocess Dataset
# ----------------------------------------

def load_and_preprocess():
    """
    Load and preprocess the Jigsaw Toxic Comment dataset.
    """

    print("\nLoading Toxicity Dataset...\n")

    dataset = load_dataset(
        "thesofakillers/jigsaw-toxic-comment-classification-challenge"
    )

    df = dataset["train"].to_pandas()

    print(f"Original Dataset Shape : {df.shape}")

    # ----------------------------------------
    # Remove Duplicate Rows
    # ----------------------------------------

    df.drop_duplicates(inplace=True)

    # ----------------------------------------
    # Remove Missing Values
    # ----------------------------------------

    df.dropna(inplace=True)

    # ----------------------------------------
    # Clean Text
    # ----------------------------------------

    df["comment_text"] = df["comment_text"].apply(clean_text)

    # ----------------------------------------
    # Remove Empty Comments
    # ----------------------------------------

    df = df[df["comment_text"].str.strip() != ""]

    # ----------------------------------------
    # Reset Index
    # ----------------------------------------

    df.reset_index(
        drop=True,
        inplace=True
    )

    print(f"Processed Dataset Shape : {df.shape}")

    # ----------------------------------------
    # Label Statistics
    # ----------------------------------------

    print("\nLabel Distribution\n")

    print(
        df[
            [
                "toxic",
                "severe_toxic",
                "obscene",
                "threat",
                "insult",
                "identity_hate"
            ]
        ].sum()
    )

    print("\nDataset Ready For Training\n")

    return df


# ----------------------------------------
# Test
# ----------------------------------------

if __name__ == "__main__":

    dataframe = load_and_preprocess()

    print("\nFirst Five Records\n")

    print(dataframe.head())