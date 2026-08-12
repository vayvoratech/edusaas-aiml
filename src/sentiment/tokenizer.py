from transformers import AutoTokenizer

from src.sentiment.data_preprocessing import (
    preprocess_data,
    split_data,
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

MODEL_NAME = "distilbert-base-uncased"


# --------------------------------------------------
# LOAD TOKENIZER
# --------------------------------------------------

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


# --------------------------------------------------
# TOKENIZE TEXT
# --------------------------------------------------

def tokenize_texts(texts):

    return tokenizer(
        texts.tolist(),
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt",
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    df = preprocess_data()

    train_df, val_df, test_df = split_data(df)

    print("\nTokenizing training data...")

    train_encodings = tokenize_texts(
        train_df["post_text"]
    )

    print("\n✅ Tokenization completed!")

    print("\nAvailable Model Inputs:")
    print(train_encodings.keys())

    print("\nInput IDs Shape:")
    print(train_encodings["input_ids"].shape)

    print("\nAttention Mask Shape:")
    print(train_encodings["attention_mask"].shape)

    print("\nOriginal Sentence:")
    print(train_df.iloc[0]["post_text"])

    print("\nTokens:")
    print(
        tokenizer.tokenize(
            train_df.iloc[0]["post_text"]
        )
    )

    print("\nInput IDs:")
    print(
        train_encodings["input_ids"][0]
    )

    print("\nAttention Mask:")
    print(
        train_encodings["attention_mask"][0]
    )