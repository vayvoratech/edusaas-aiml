import torch

from transformers import (
    AutoTokenizer,
    DistilBertForSequenceClassification
)

# ---------------------------------------
# Load Saved Model
# ---------------------------------------

MODEL_PATH = "models/sentiment"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH
)

model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_PATH
)

model.eval()
# ---------------------------------------
# Label Mapping
# ---------------------------------------

LABELS = {

    0: "NEGATIVE",

    1: "NEUTRAL",

    2: "POSITIVE"

}

# ---------------------------------------
# Prediction Function
# ---------------------------------------

def predict_sentiment(text):

    encoding = tokenizer(

        text,

        return_tensors="pt",

        truncation=True,

        padding=True

    )

    with torch.no_grad():

        outputs = model(**encoding)

    probabilities = torch.softmax(

        outputs.logits,

        dim=1

    )

    confidence, prediction = torch.max(

        probabilities,

        dim=1

    )

    return {

        "text": text,

        "prediction": LABELS[prediction.item()],

        "confidence": round(

            confidence.item(),

            4

        )

    }

# ---------------------------------------
# Testing
# ---------------------------------------

if __name__ == "__main__":

    samples = [

        "This course is amazing.",

        "I hate this lesson.",

        "The assignment is due tomorrow."

    ]

    for sentence in samples:

        print()

        print(

            predict_sentiment(sentence)

        )