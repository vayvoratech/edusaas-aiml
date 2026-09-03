import pandas as pd


class HiringDataset:
    """
    Prepare Predictive Hiring dataset for ML training.
    """

    FEATURE_COLUMNS = [

        "experience_years",

        "required_experience_years",

        "skill_match_score",

        "experience_match_score",

        "domain_match",

        "profile_score"

    ]

    TARGET_COLUMN = "matched"

    def __init__(
        self,
        dataframe: pd.DataFrame
    ):

        self.dataframe = dataframe.copy()

    def prepare(self):

        missing = [

            column

            for column in self.FEATURE_COLUMNS
            + [self.TARGET_COLUMN]

            if column not in self.dataframe.columns

        ]

        if missing:

            raise ValueError(
                f"Missing columns: {missing}"
            )

        X = self.dataframe[
            self.FEATURE_COLUMNS
        ].copy()

        y = self.dataframe[
            self.TARGET_COLUMN
        ].copy()

        return X, y


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    dataframe = pd.read_csv(
        "data/hiring/"
        "hiring_training_dataset.csv"
    )

    dataset = HiringDataset(
        dataframe
    )

    X, y = dataset.prepare()

    print(
        "\nFeature Shape:",
        X.shape
    )

    print(
        "Target Shape:",
        y.shape
    )

    print(
        "\nFeatures:"
    )

    print(
        X.columns.tolist()
    )

    print(
        "\nTarget Distribution:"
    )

    print(
        y.value_counts()
    )