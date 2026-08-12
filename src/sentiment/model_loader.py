from transformers import (
    AutoTokenizer,
    DistilBertForSequenceClassification
)

import torch

MODEL_PATH = "models/sentiment"


class SentimentModel:

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance.tokenizer = AutoTokenizer.from_pretrained(
                MODEL_PATH
            )

            cls._instance.model = DistilBertForSequenceClassification.from_pretrained(
                MODEL_PATH
            )

            cls._instance.model.eval()

        return cls._instance


model_loader = SentimentModel()