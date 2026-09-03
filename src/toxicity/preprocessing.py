import re

from datasets import load_dataset


LABEL_COLUMNS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]


def clean_text(text: str) -> str:
    """
    Clean a single text input.
    Used by both training and inference.
    """

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text,
    )

    text = re.sub(
        r"<[^>]+>",
        " ",
        text,
    )

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def load_and_preprocess():
    """
    Load the Jigsaw toxicity dataset and preprocess it.
    """

    print("\nLoading Toxicity Dataset...\n")

    dataset = load_dataset(
        "thesofakillers/jigsaw-toxic-comment-classification-challenge"
    )

    df = dataset["train"].to_pandas()

    print(f"Original Dataset Shape: {df.shape}")

    # Remove duplicates
    df = df.drop_duplicates(
        subset=["comment_text"]
    ).copy()

    print(f"After duplicates removed: {df.shape}")

    # Remove missing comments
    df = df.dropna(
        subset=["comment_text"]
    ).copy()

    # Convert once to string
    df["comment_text"] = df["comment_text"].astype(str)

    print("Cleaning text...")

    # Vectorized string operations.
    # Much faster than Series.apply(clean_text).

    df["comment_text"] = (
        df["comment_text"]
        .str.lower()
        .str.replace(
            r"https?://\S+|www\.\S+",
            " ",
            regex=True,
        )
        .str.replace(
            r"<[^>]+>",
            " ",
            regex=True,
        )
        .str.replace(
            r"[^a-zA-Z0-9\s]",
            " ",
            regex=True,
        )
        .str.replace(
            r"\s+",
            " ",
            regex=True,
        )
        .str.strip()
    )

    # Remove empty comments
    df = df[
        df["comment_text"].str.len() > 0
    ].copy()

    df.reset_index(
        drop=True,
        inplace=True,
    )

    print(
        f"Processed Dataset Shape: {df.shape}"
    )

    print("\nLabel Distribution:\n")

    print(
        df[LABEL_COLUMNS].sum()
    )

    print("\nDataset preprocessing completed.\n")

    return df


if __name__ == "__main__":

    dataframe = load_and_preprocess()

    print("\nFirst 5 records:\n")

    print(
        dataframe[
            ["comment_text"] + LABEL_COLUMNS
        ].head()
    )

    print("\nCleaning test:\n")

    test_text = """
    You are an idiot!!! Visit https://example.com
    """

    print("Original:")
    print(test_text)

    print("\nCleaned:")
    print(clean_text(test_text))