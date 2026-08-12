import os
import torch
import numpy as np

from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW

from transformers import (
    AutoTokenizer,
    DistilBertForSequenceClassification
)
from sklearn.metrics import accuracy_score

from src.sentiment.data_preprocessing import (
    preprocess_data,
    split_data
)

device = torch.device(

    "cuda"

    if torch.cuda.is_available()

    else "cpu"

)

print(f"Using Device : {device}")

df = preprocess_data()

train_df, val_df, test_df = split_data(df)

tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased"
)

train_encodings = tokenizer(

    train_df["post_text"].tolist(),

    truncation=True,

    padding=True,

    return_tensors="pt"

)

val_encodings = tokenizer(

    val_df["post_text"].tolist(),

    truncation=True,

    padding=True,

    return_tensors="pt"

)

class SentimentDataset(Dataset):

    def __init__(self, encodings, labels):

        self.encodings = encodings
        self.labels = labels

    def __len__(self):

        return len(self.labels)

    def __getitem__(self, idx):

        item = {
            key: value[idx]
            for key, value in self.encodings.items()
        }

        item["labels"] = torch.tensor(
            self.labels[idx]
        )

        return item


# ---------------------------------------
# Create Dataset
# ---------------------------------------

train_dataset = SentimentDataset(
    train_encodings,
    train_df["label"].tolist()
)

val_dataset = SentimentDataset(
    val_encodings,
    val_df["label"].tolist()
)


# ---------------------------------------
# DataLoader
# ---------------------------------------

train_loader = DataLoader(
    train_dataset,
    batch_size=8,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=8
)

# ---------------------------------------
# Load DistilBERT Model
# ---------------------------------------

model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=3
)

model.to(device)

# ---------------------------------------
# Optimizer
# ---------------------------------------

optimizer = AdamW(
    model.parameters(),
    lr=2e-5
)

# ---------------------------------------
# Training Settings
# ---------------------------------------

EPOCHS = 3

# ---------------------------------------
# Training Loop
# ---------------------------------------

for epoch in range(EPOCHS):

    model.train()

    total_loss = 0

    print(f"\nEpoch {epoch+1}/{EPOCHS}")

    for batch in train_loader:

        optimizer.zero_grad()

        input_ids = batch["input_ids"].to(device)

        attention_mask = batch["attention_mask"].to(device)

        labels = batch["labels"].to(device)

        outputs = model(

            input_ids=input_ids,

            attention_mask=attention_mask,

            labels=labels

        )

        loss = outputs.loss

        total_loss += loss.item()

        loss.backward()

        optimizer.step()

    avg_loss = total_loss / len(train_loader)

    print(f"Training Loss : {avg_loss:.4f}")

    # ---------------------------------------
# Validation
# ---------------------------------------

    model.eval()

    predictions = []

    actual_labels = []

    with torch.no_grad():

        for batch in val_loader:

            input_ids = batch["input_ids"].to(device)

            attention_mask = batch["attention_mask"].to(device)

            labels = batch["labels"].to(device)

            outputs = model(

                input_ids=input_ids,

                attention_mask=attention_mask

            )

            preds = torch.argmax(

                outputs.logits,

                dim=1

            )

            predictions.extend(

                preds.cpu().numpy()

            )

            actual_labels.extend(

                labels.cpu().numpy()

            )

    accuracy = accuracy_score(

        actual_labels,

        predictions

    )

    print(

        f"Validation Accuracy : {accuracy:.4f}"

    )

    # ---------------------------------------
# Save Model
# ---------------------------------------

SAVE_PATH = "models/sentiment"

os.makedirs(

    SAVE_PATH,

    exist_ok=True

)

model.save_pretrained(SAVE_PATH)

tokenizer.save_pretrained(SAVE_PATH)

print("\nModel Saved Successfully!")