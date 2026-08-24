import pandas as pd


def clean_dropout_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # ========================================================
    # Remove duplicate records
    # ========================================================

    df = df.drop_duplicates()


    # ========================================================
    # Numeric missing values
    # ========================================================

    numeric_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns


    for column in numeric_columns:

        if df[column].isnull().sum() > 0:

            df[column] = df[column].fillna(
                df[column].median()
            )


    # ========================================================
    # Validate feature ranges
    # ========================================================

    if "completion_percentage" in df.columns:

        df["completion_percentage"] = (
            df["completion_percentage"]
            .clip(0, 100)
        )


    if "quiz_average" in df.columns:

        df["quiz_average"] = (
            df["quiz_average"]
            .clip(0, 100)
        )


    if "assignment_completion_rate" in df.columns:

        df["assignment_completion_rate"] = (
            df["assignment_completion_rate"]
            .clip(0, 100)
        )


    return df