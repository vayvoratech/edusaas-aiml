import os
import random

import numpy as np
import torch

from sklearn.model_selection import train_test_split

from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)

from src.toxicity.preprocessing import load_and_preprocess
from src.toxicity.toxicity_dataset import ToxicityDataset
from src.toxicity.evaluate_model import evaluate_model


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "distilbert-base-uncased"

MODEL_PATH = "models/toxicity"

MAX_LENGTH = 256

BATCH_SIZE = 8

EPOCHS = 1

LEARNING_RATE = 2e-5

VALIDATION_SIZE = 0.20

SEED = 42

NUM_LABELS = 6


# ============================================================
# Training Dataset Size
# ============================================================
#
# Development:
#     USE_SAMPLE = True
#     SAMPLE_SIZE = 1000
#
# Full training:
#     USE_SAMPLE = False
#
# ============================================================

USE_SAMPLE = True

SAMPLE_SIZE = 1000


# ============================================================
# Reproducibility
# ============================================================

random.seed(SEED)

np.random.seed(SEED)

torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# ============================================================
# Load Dataset
# ============================================================

print("\n" + "=" * 60)
print("LOADING TOXICITY DATASET")
print("=" * 60)

df = load_and_preprocess()

print(
    f"\nTotal available samples: {len(df)}"
)


# ============================================================
# Development Sampling
# ============================================================

if USE_SAMPLE:

    if SAMPLE_SIZE > len(df):

        raise ValueError(
            f"SAMPLE_SIZE={SAMPLE_SIZE} is greater "
            f"than available samples={len(df)}"
        )

    print(
        f"\nDevelopment mode enabled."
    )

    print(
        f"Using {SAMPLE_SIZE} samples."
    )

    df = df.sample(
        n=SAMPLE_SIZE,
        random_state=SEED,
    ).reset_index(drop=True)

else:

    print(
        "\nFull dataset training enabled."
    )

    df = df.reset_index(
        drop=True
    )


print(
    f"Dataset used for training: {len(df)}"
)


# ============================================================
# Train / Validation Split
# ============================================================

train_df, val_df = train_test_split(

    df,

    test_size=VALIDATION_SIZE,

    random_state=SEED,

    shuffle=True,
)


print(
    f"\nTraining Samples   : {len(train_df)}"
)

print(
    f"Validation Samples : {len(val_df)}"
)


# ============================================================
# Load Tokenizer
# ============================================================

print("\n" + "=" * 60)
print("LOADING TOKENIZER")
print("=" * 60)

tokenizer = DistilBertTokenizerFast.from_pretrained(
    MODEL_NAME
)


# ============================================================
# Create PyTorch Datasets
# ============================================================

print("\nCreating training dataset...")

train_dataset = ToxicityDataset(

    dataframe=train_df,

    tokenizer=tokenizer,

    max_length=MAX_LENGTH,
)


print("Creating validation dataset...")

val_dataset = ToxicityDataset(

    dataframe=val_df,

    tokenizer=tokenizer,

    max_length=MAX_LENGTH,
)


# ============================================================
# Load DistilBERT
# ============================================================

print("\n" + "=" * 60)
print("LOADING DISTILBERT MODEL")
print("=" * 60)

model = DistilBertForSequenceClassification.from_pretrained(

    MODEL_NAME,

    num_labels=NUM_LABELS,

    problem_type="multi_label_classification",
)


# ============================================================
# Training Arguments
# ============================================================

training_args = TrainingArguments(

    output_dir=MODEL_PATH,

    do_train=True,

    do_eval=True,

    eval_strategy="epoch",

    save_strategy="epoch",

    num_train_epochs=EPOCHS,

    per_device_train_batch_size=BATCH_SIZE,

    per_device_eval_batch_size=BATCH_SIZE,

    learning_rate=LEARNING_RATE,

    weight_decay=0.01,

    logging_steps=50,

    save_total_limit=2,

    load_best_model_at_end=True,

    metric_for_best_model="eval_loss",

    greater_is_better=False,

    report_to="none",

    use_cpu=True,

)


# ============================================================
# Trainer
# ============================================================

trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=val_dataset,

    compute_metrics=evaluate_model,
)


# ============================================================
# Train Model
# ============================================================

print("\n" + "=" * 60)
print("STARTING TOXICITY MODEL TRAINING")
print("=" * 60)

trainer.train()


print("\nTraining Completed Successfully.")


# ============================================================
# Evaluate Model
# ============================================================

print("\n" + "=" * 60)
print("EVALUATING MODEL")
print("=" * 60)

metrics = trainer.evaluate()

print("\nEvaluation Metrics:")

for key, value in metrics.items():

    print(
        f"{key}: {value}"
    )


# ============================================================
# Save Model
# ============================================================

print("\n" + "=" * 60)
print("SAVING MODEL")
print("=" * 60)

os.makedirs(
    MODEL_PATH,
    exist_ok=True,
)

trainer.save_model(
    MODEL_PATH
)

tokenizer.save_pretrained(
    MODEL_PATH
)


print(
    "\nModel Saved Successfully."
)

print(
    f"Location: {MODEL_PATH}"
)