from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification
)

MODEL_PATH = "models/toxicity"


class ToxicityModelLoader:

    def __init__(self):

        self.tokenizer = DistilBertTokenizerFast.from_pretrained(
            MODEL_PATH
        )

        self.model = DistilBertForSequenceClassification.from_pretrained(
            MODEL_PATH
        )

        self.model.eval()


model_loader = ToxicityModelLoader()