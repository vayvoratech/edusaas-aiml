import os
import pandas as pd
import torch

from torch import nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW

from transformers import (
    XLNetModel,
    XLNetTokenizer
)

from sklearn.model_selection import train_test_split


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "xlnet-base-cased"

DATASET_PATH = "descriptive_answers.csv"

OUTPUT_MODEL = "xlnet_answer_assessment_model.pt"

MAX_LENGTH = 512

BATCH_SIZE = 4

EPOCHS = 3

LEARNING_RATE = 2e-5


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", DEVICE)


# ============================================================
# Dataset
# ============================================================

class AnswerDataset(Dataset):

    def __init__(
        self,
        dataframe,
        tokenizer,
        max_length=512
    ):

        self.data = dataframe.reset_index(drop=True)

        self.tokenizer = tokenizer

        self.max_length = max_length


    def __len__(self):

        return len(self.data)


    def __getitem__(self, index):

        row = self.data.iloc[index]

        question = str(row["question"])

        reference_answer = str(
            row["reference_answer"]
        )

        student_answer = str(
            row["student_answer"]
        )

        score = float(row["score"])


        # Same input format as your current model
        combined_text = (
            f"{question} [SEP] "
            f"{student_answer} [SEP] "
            f"{reference_answer}"
        )


        encoding = self.tokenizer(
            combined_text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )


        return {

            "input_ids":
                encoding["input_ids"].squeeze(0),

            "attention_mask":
                encoding["attention_mask"].squeeze(0),

            "token_type_ids":
                encoding.get(
                    "token_type_ids",
                    torch.zeros_like(
                        encoding["input_ids"]
                    )
                ).squeeze(0),

            "score":
                torch.tensor(
                    score,
                    dtype=torch.float
                )
        }


# ============================================================
# Model
# ============================================================

class XLNetAnswerAssessmentModel(nn.Module):

    def __init__(self):

        super(
            XLNetAnswerAssessmentModel,
            self
        ).__init__()


        self.xlnet = XLNetModel.from_pretrained(
            MODEL_NAME
        )


        hidden_size = 768


        self.dense1 = nn.Linear(
            hidden_size,
            256
        )


        self.dense2 = nn.Linear(
            256,
            64
        )


        self.output = nn.Linear(
            64,
            1
        )


    def forward(
        self,
        input_ids,
        attention_mask=None,
        token_type_ids=None
    ):

        outputs = self.xlnet(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )


        hidden_states = outputs.last_hidden_state


        pooled = torch.mean(
            hidden_states,
            dim=1
        )


        x = torch.relu(
            self.dense1(pooled)
        )


        x = torch.relu(
            self.dense2(x)
        )


        x = torch.sigmoid(
            self.output(x)
        )


        return x.squeeze(-1)


# ============================================================
# Load dataset
# ============================================================

print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)


required_columns = [
    "question",
    "reference_answer",
    "student_answer",
    "score"
]


for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Missing column: {column}"
        )


# Remove missing data

df = df.dropna(
    subset=required_columns
)


# Make sure score is between 0 and 1

df["score"] = df["score"].astype(float)


df["score"] = df["score"].clip(
    0.0,
    1.0
)


print(
    "Total samples:",
    len(df)
)


# ============================================================
# Train / Validation split
# ============================================================

train_df, val_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42
)


print(
    "Training samples:",
    len(train_df)
)

print(
    "Validation samples:",
    len(val_df)
)


# ============================================================
# Tokenizer
# ============================================================

print("Loading tokenizer...")

tokenizer = XLNetTokenizer.from_pretrained(
    MODEL_NAME
)


# ============================================================
# Dataset / DataLoader
# ============================================================

train_dataset = AnswerDataset(
    train_df,
    tokenizer,
    MAX_LENGTH
)


val_dataset = AnswerDataset(
    val_df,
    tokenizer,
    MAX_LENGTH
)


train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)


val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# ============================================================
# Model
# ============================================================

print("Loading XLNet model...")

model = XLNetAnswerAssessmentModel()

model.to(DEVICE)


# ============================================================
# Loss + Optimizer
# ============================================================

criterion = nn.MSELoss()


optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE
)


# ============================================================
# Training
# ============================================================

for epoch in range(EPOCHS):

    print(
        f"\n========== Epoch {epoch + 1}/{EPOCHS} =========="
    )


    model.train()

    total_loss = 0


    for batch in train_loader:

        input_ids = batch[
            "input_ids"
        ].to(DEVICE)


        attention_mask = batch[
            "attention_mask"
        ].to(DEVICE)


        token_type_ids = batch[
            "token_type_ids"
        ].to(DEVICE)


        scores = batch[
            "score"
        ].to(DEVICE)


        optimizer.zero_grad()


        predictions = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )


        loss = criterion(
            predictions,
            scores
        )


        loss.backward()


        optimizer.step()


        total_loss += loss.item()


    avg_train_loss = (
        total_loss /
        len(train_loader)
    )


    print(
        "Training Loss:",
        avg_train_loss
    )


    # ========================================================
    # Validation
    # ========================================================

    model.eval()

    val_loss = 0


    with torch.no_grad():

        for batch in val_loader:

            input_ids = batch[
                "input_ids"
            ].to(DEVICE)


            attention_mask = batch[
                "attention_mask"
            ].to(DEVICE)


            token_type_ids = batch[
                "token_type_ids"
            ].to(DEVICE)


            scores = batch[
                "score"
            ].to(DEVICE)


            predictions = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids
            )


            loss = criterion(
                predictions,
                scores
            )


            val_loss += loss.item()


    avg_val_loss = (
        val_loss /
        len(val_loader)
    )


    print(
        "Validation Loss:",
        avg_val_loss
    )


# ============================================================
# Save model
# ============================================================

print("\nSaving model...")

torch.save(
    model.state_dict(),
    OUTPUT_MODEL
)


print(
    f"Model saved to: {OUTPUT_MODEL}"
)