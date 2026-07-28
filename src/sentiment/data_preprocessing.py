from sklearn.model_selection import train_test_split

from src.sentiment.load_data import load_sentiment_data


# --------------------------------------------------
# LABEL MAPPING
# --------------------------------------------------

LABEL_MAP = {
    "NEGATIVE": 0,
    "NEUTRAL": 1,
    "POSITIVE": 2,
}


# --------------------------------------------------
# PREPROCESS DATA
# --------------------------------------------------

def preprocess_data():

    # Load data from PostgreSQL
    df = load_sentiment_data()

    print("\nOriginal Dataset Shape:")
    print(df.shape)

    # ----------------------------------------------
    # 1. Remove missing values
    # ----------------------------------------------

    df = df.dropna(
        subset=["post_text", "sentiment"]
    )

    # ----------------------------------------------
    # 2. Convert text to string and remove spaces
    # ----------------------------------------------

    df["post_text"] = (
        df["post_text"]
        .astype(str)
        .str.strip()
    )

    # ----------------------------------------------
    # 3. Remove empty posts
    # ----------------------------------------------

    df = df[
        df["post_text"] != ""
    ]

    # ----------------------------------------------
    # 4. Standardize sentiment labels
    # ----------------------------------------------

    df["sentiment"] = (
        df["sentiment"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # ----------------------------------------------
    # 5. Keep only valid labels
    # ----------------------------------------------

    df = df[
        df["sentiment"].isin(
            LABEL_MAP.keys()
        )
    ]

    # ----------------------------------------------
    # 6. Remove duplicate text
    # ----------------------------------------------

    df = df.drop_duplicates(
        subset=["post_text"]
    )

    # ----------------------------------------------
    # 7. Convert labels to numbers
    # ----------------------------------------------

    df["label"] = (
        df["sentiment"]
        .map(LABEL_MAP)
    )

    # Reset index
    df = df.reset_index(drop=True)

    print("\nCleaned Dataset Shape:")
    print(df.shape)

    print("\nLabel Distribution:")
    print(df["sentiment"].value_counts())

    print("\nSample:")
    print(
        df[
            ["post_text", "sentiment", "label"]
        ].head()
    )

    return df


# --------------------------------------------------
# SPLIT DATA
# --------------------------------------------------

def split_data(df):

    # 80% Training
    # 20% Temporary

    train_df, temp_df = train_test_split(
        df,
        test_size=0.20,
        random_state=42,
        stratify=df["label"],
    )

    # Split temporary data:
    # 10% Validation
    # 10% Test

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["label"],
    )

    return train_df, val_df, test_df


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    df = preprocess_data()

    train_df, val_df, test_df = split_data(df)

    print("\n--------------------------------")
    print("DATA SPLIT")
    print("--------------------------------")

    print("Training Records:", len(train_df))
    print("Validation Records:", len(val_df))
    print("Testing Records:", len(test_df))

    print("\nTraining Distribution:")
    print(train_df["sentiment"].value_counts())

    print("\nValidation Distribution:")
    print(val_df["sentiment"].value_counts())

    print("\nTesting Distribution:")
    print(test_df["sentiment"].value_counts())

    print("\n✅ Sentiment preprocessing completed!")