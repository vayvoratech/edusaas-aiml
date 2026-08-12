import torch
from torch.utils.data import Dataset


class ToxicityDataset(Dataset):
    """
    PyTorch Dataset for Toxicity Detection.
    Converts comments into BERT-compatible tensors.
    """

    LABEL_COLUMNS = [
        "toxic",
        "severe_toxic",
        "obscene",
        "threat",
        "insult",
        "identity_hate"
    ]

    def __init__(
        self,
        dataframe,
        tokenizer,
        max_length=256
    ):

        self.data = dataframe.reset_index(drop=True)

        self.tokenizer = tokenizer

        self.max_length = max_length

    def __len__(self):

        return len(self.data)

    def __getitem__(self, index):

        row = self.data.iloc[index]

        comment = str(row["comment_text"])

        labels = row[
            self.LABEL_COLUMNS
        ].astype(float).values

        encoding = self.tokenizer(

            comment,

            truncation=True,

            padding="max_length",

            max_length=self.max_length,

            return_tensors="pt"

        )

        return {

            "input_ids": encoding["input_ids"].squeeze(0),

            "attention_mask": encoding["attention_mask"].squeeze(0),

            "labels": torch.tensor(
                labels,
                dtype=torch.float32
            )

        }