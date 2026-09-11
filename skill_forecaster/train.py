# train.py
import os
import joblib
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error

DATA_FILE = "data/weekly_skill_panel.csv"
MODEL_DIR = "models"
MODEL_FILE = os.path.join(MODEL_DIR, "skill_lgbm_model.joblib")
METADATA_FILE = os.path.join(MODEL_DIR, "model_metadata.joblib")

def load_and_clean_data(file_path):
    """Loads CSV, standardizes column formats, and drops incomplete trailing months."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing {file_path}. Place your dataset into the data/ folder.")

    df = pd.read_csv(file_path)
    df.columns = [c.lower().strip().replace('"', '') for c in df.columns]

    if "tagname" in df.columns:
        df.rename(columns={"tagname": "skill_abr"}, inplace=True)
    if "count" in df.columns:
        df.rename(columns={"count": "skill_count"}, inplace=True)

    df["date"] = pd.to_datetime(df["date"].astype(str).str.replace('"', '').str.strip())
    df["skill_abr"] = df["skill_abr"].astype(str).str.replace('"', '').str.strip().str.lower()
    df["skill_count"] = (
        df["skill_count"]
        .astype(str)
        .str.replace('"', '')
        .str.strip()
        .astype(int)
    )

    # Filter out the final/ongoing incomplete month to eliminate denominator artifacts
    latest_month = df["date"].max()
    df = df[df["date"] < latest_month].copy()

    return df

def engineer_share_features(df):
    """Normalizes raw count into % market share and engineers temporal features."""
    unique_dates = np.sort(df["date"].unique())
    all_skills = sorted(df["skill_abr"].unique())

    # Build balanced grid so missing months get 0 count
    grid_idx = pd.MultiIndex.from_product([unique_dates, all_skills], names=["date", "skill_abr"])
    df = (
        df.set_index(["date", "skill_abr"])
        .reindex(grid_idx, fill_value=0)
        .reset_index()
        .sort_values(["skill_abr", "date"])
        .reset_index(drop=True)
    )

    # Calculate Market Share (%)
    monthly_totals = df.groupby("date")["skill_count"].transform("sum")
    df["skill_share"] = (df["skill_count"] / monthly_totals.replace(0, 1)) * 100

    # Lags (1, 2, and 3 months ago)
    for lag in [1, 2, 3]:
        df[f"lag_share_{lag}"] = df.groupby("skill_abr")["skill_share"].shift(lag)

    # Momentum and short-term rolling mean
    df["momentum_1_3"] = df["lag_share_1"] - df["lag_share_3"]
    df["rolling_share_3m"] = (
        df.groupby("skill_abr")["skill_share"]
        .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    df["skill_cat"] = pd.Categorical(df["skill_abr"], categories=all_skills)
    return df.dropna().reset_index(drop=True), all_skills

def train_and_export():
    os.makedirs(MODEL_DIR, exist_ok=True)
    raw_df = load_and_clean_data(DATA_FILE)
    feat_df, categories = engineer_share_features(raw_df)

    # Chronological Split (80% Train, 20% Test)
    all_dates = np.sort(feat_df["date"].unique())
    cutoff = all_dates[int(len(all_dates) * 0.8)]

    train = feat_df[feat_df["date"] < cutoff].copy()
    test = feat_df[feat_df["date"] >= cutoff].copy()

    features = ["skill_cat", "lag_share_1", "lag_share_2", "lag_share_3", "momentum_1_3", "rolling_share_3m"]
    target = "skill_share"

    X_train, y_train = train[features], train[target]
    X_test, y_test = test[features], test[target]

    # Constrained LightGBM model to prevent trend overfitting
    model = lgb.LGBMRegressor(
        n_estimators=150,
        learning_rate=0.03,
        max_depth=3,
        num_leaves=15,
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)

    print(f"\n==========================================")
    print(f" Model Trained on Cleaned Market Share (%)")
    print(f" Skills Tracked: {len(categories)}")
    print(f" Range: {raw_df['date'].min().strftime('%Y-%m')} to {raw_df['date'].max().strftime('%Y-%m')}")
    print(f" Out-of-Sample MAE: {mae:.3f}% share error")
    print(f"==========================================")

    # Save artifacts
    joblib.dump(model, MODEL_FILE)
    meta = {
        "features": features,
        "categories": categories,
        "available_skills": categories
    }
    joblib.dump(meta, METADATA_FILE)
    print(f"Artifacts successfully saved to '{MODEL_DIR}/'.")

if __name__ == "__main__":
    train_and_export()