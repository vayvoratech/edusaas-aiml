import pandas as pd


class HiringPreprocessor:
    """
    Load and validate the Predictive Hiring training dataset.
    """

    REQUIRED_COLUMNS = [

        "user_id",
        "job_id",

        "experience_years",
        "required_experience_years",

        "skill_match_score",
        "experience_match_score",

        "domain_match",
        "profile_score",

        "match_score",
        "matched"
    ]

    def __init__(self, dataframe: pd.DataFrame):

        self.dataframe = dataframe.copy()

    def preprocess(self) -> pd.DataFrame:

        dataframe = self.dataframe.copy()

        print("\nPreprocessing Hiring Dataset...\n")

        # --------------------------------------------------
        # Validate columns
        # --------------------------------------------------

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:

            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        # --------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------

        before = len(dataframe)

        dataframe.drop_duplicates(
            subset=[
                "user_id",
                "job_id"
            ],
            inplace=True
        )

        print(
            f"Duplicates Removed : "
            f"{before - len(dataframe)}"
        )

        # --------------------------------------------------
        # Handle missing values
        # --------------------------------------------------

        numeric_columns = [

            "experience_years",
            "required_experience_years",
            "skill_match_score",
            "experience_match_score",
            "domain_match",
            "profile_score",
            "match_score",
            "matched"

        ]

        for column in numeric_columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )

        dataframe[numeric_columns] = (
            dataframe[numeric_columns]
            .fillna(0)
        )

        # --------------------------------------------------
        # Clip values
        # --------------------------------------------------

        dataframe["skill_match_score"] = (
            dataframe["skill_match_score"]
            .clip(0, 1)
        )

        dataframe["experience_match_score"] = (
            dataframe["experience_match_score"]
            .clip(0, 1)
        )

        dataframe["profile_score"] = (
            dataframe["profile_score"]
            .clip(0, 100)
        )

        dataframe["match_score"] = (
            dataframe["match_score"]
            .clip(0, 1)
        )

        dataframe["domain_match"] = (
            dataframe["domain_match"]
            .clip(0, 1)
            .astype(int)
        )

        dataframe["matched"] = (
            dataframe["matched"]
            .clip(0, 1)
            .astype(int)
        )

        # --------------------------------------------------
        # Reset index
        # --------------------------------------------------

        dataframe.reset_index(
            drop=True,
            inplace=True
        )

        print(
            f"Final Dataset Shape : "
            f"{dataframe.shape}"
        )

        print(
            "\nTarget Distribution:"
        )

        print(
            dataframe["matched"]
            .value_counts()
        )

        return dataframe


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    dataframe = pd.read_csv(
        "data/hiring/"
        "hiring_training_dataset.csv"
    )

    processor = HiringPreprocessor(
        dataframe
    )

    dataframe = processor.preprocess()

    print(
        "\nDataset Preview:\n"
    )

    print(
        dataframe.head()
    )