import pandas as pd
from sqlalchemy import create_engine


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# LOAD SENTIMENT DATA
# --------------------------------------------------

def load_sentiment_data():

    query = """
        SELECT
            post_id,
            post_text,
            sentiment
        FROM discussion_posts
        WHERE post_text IS NOT NULL
          AND sentiment IS NOT NULL
    """

    df = pd.read_sql(query, engine)

    return df


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    df = load_sentiment_data()

    print("\nDataset loaded successfully!")
    print("Dataset Shape:", df.shape)

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Posts:")
    print(df["post_text"].duplicated().sum())

    print("\nSentiment Distribution:")
    print(df["sentiment"].value_counts())

    print("\nSentiment Percentage:")
    print(
        df["sentiment"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )