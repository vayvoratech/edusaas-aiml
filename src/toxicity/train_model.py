import os
import random
import numpy as np
import torch

from sklearn.model_selection import train_test_split

from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)

from src.toxicity.preprocessing import load_and_preprocess
from src.toxicity.toxicity_dataset import ToxicityDataset
from src.toxicity.evaluate_model import evaluate_model


# ----------------------------------------
# Configuration
# ----------------------------------------

MODEL_NAME = "distilbert-base-uncased"

MODEL_PATH = "models/toxicity"

MAX_LENGTH = 256

BATCH_SIZE = 8

EPOCHS = 1

SEED = 42


# ----------------------------------------
# Set Random Seed
# ----------------------------------------

random.seed(SEED)

np.random.seed(SEED)

torch.manual_seed(SEED)


# ----------------------------------------
# Load Dataset
# ----------------------------------------

print("\nLoading Toxicity Dataset...\n")

df = load_and_preprocess()

# -------------------------------------------------
# Development Only
# Remove this line for Production Training
# -------------------------------------------------

df = df.sample(
    n=1000,
    random_state=SEED
).reset_index(drop=True)

train_df, val_df = train_test_split(

    df,

    test_size=0.20,

    random_state=SEED,

    shuffle=True

)

print(f"Training Samples   : {len(train_df)}")

print(f"Validation Samples : {len(val_df)}")


# ----------------------------------------
# Load Tokenizer
# ----------------------------------------

print("\nLoading Tokenizer...\n")

tokenizer = DistilBertTokenizerFast.from_pretrained(
    MODEL_NAME
)


# ----------------------------------------
# Create Dataset
# ----------------------------------------

train_dataset = ToxicityDataset(

    train_df,

    tokenizer,

    MAX_LENGTH

)

val_dataset = ToxicityDataset(

    val_df,

    tokenizer,

    MAX_LENGTH

)


# ----------------------------------------
# Load Model
# ----------------------------------------

print("\nLoading DistilBERT Model...\n")

model = DistilBertForSequenceClassification.from_pretrained(

    MODEL_NAME,

    num_labels=6,

    problem_type="multi_label_classification"

)


# ----------------------------------------
# Training Arguments
# ----------------------------------------

training_args = TrainingArguments(

    output_dir=MODEL_PATH,

    do_train=True,

    do_eval=True,

    eval_strategy="epoch",

    save_strategy="epoch",

    num_train_epochs=EPOCHS,

    per_device_train_batch_size=BATCH_SIZE,

    per_device_eval_batch_size=BATCH_SIZE,

    learning_rate=2e-5,

    weight_decay=0.01,

    logging_steps=100,

    save_total_limit=2,

    load_best_model_at_end=True,

    report_to="none",

    use_cpu=True

)


# ----------------------------------------
# Trainer
# ----------------------------------------

trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=val_dataset,

    compute_metrics=evaluate_model

)


# ----------------------------------------
# Train
# ----------------------------------------

print("\nStarting Toxicity Model Training...\n")

trainer.train()

print("\nTraining Completed Successfully")


# ----------------------------------------
# Evaluate
# ----------------------------------------

print("\nEvaluating Model...\n")

metrics = trainer.evaluate()

print(metrics)


# ----------------------------------------
# Save Model
# ----------------------------------------

print("\nSaving Model...\n")

os.makedirs(

    MODEL_PATH,

    exist_ok=True

)

trainer.save_model(MODEL_PATH)

tokenizer.save_pretrained(MODEL_PATH)

print("\nModel Saved Successfully")

print(f"Location : {MODEL_PATH}")