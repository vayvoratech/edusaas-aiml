import joblib

from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy


# ============================================================
# COLLABORATIVE FILTERING TRAINER
# ============================================================

class CollaborativeFilteringModel:

    def __init__(self):

        self.model = SVD(
            random_state=42
        )

        self.reader = Reader(
            rating_scale=(1, 5)
        )


    # ========================================================
    # VALIDATE RATINGS
    # ========================================================

    def validate_ratings(self, ratings):

        if ratings is None or ratings.empty:

            raise ValueError(
                "Ratings dataset cannot be empty."
            )

        required_columns = [
            "user_id",
            "course_id",
            "rating"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in ratings.columns
        ]

        if missing_columns:

            raise ValueError(
                f"Missing rating columns: "
                f"{missing_columns}"
            )


    # ========================================================
    # TRAIN
    # ========================================================

    def train(self, ratings):

        self.validate_ratings(
            ratings
        )

        data = Dataset.load_from_df(
            ratings[
                [
                    "user_id",
                    "course_id",
                    "rating"
                ]
            ],
            self.reader
        )

        trainset, testset = train_test_split(
            data,
            test_size=0.20,
            random_state=42
        )

        print()
        print(
            "Training ratings:",
            trainset.n_ratings
        )

        print(
            "Testing ratings:",
            len(testset)
        )

        self.model.fit(
            trainset
        )

        print()
        print(
            "✅ Collaborative filtering "
            "SVD model trained successfully"
        )

        predictions = self.model.test(
            testset
        )

        rmse = accuracy.rmse(
            predictions,
            verbose=True
        )

        print(
            f"✅ Collaborative Filtering "
            f"RMSE: {rmse:.4f}"
        )

        return self.model


    # ========================================================
    # PREDICT
    # ========================================================

    def predict(
        self,
        user_id,
        course_id
    ):

        prediction = self.model.predict(
            str(user_id),
            str(course_id)
        )

        return float(
            prediction.est
        )


    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        path="models/svd_recommendation_model.pkl"
    ):

        joblib.dump(
            self.model,
            path
        )

        print(
            f"✅ SVD model saved: {path}"
        )


# ============================================================
# FACTORY
# ============================================================

def create_collaborative_model():

    return CollaborativeFilteringModel()