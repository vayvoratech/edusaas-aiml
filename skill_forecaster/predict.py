# predict.py
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DATA_FILE = "data/weekly_skill_panel.csv"
MODEL_FILE = "models/skill_lgbm_model.joblib"
METADATA_FILE = "models/model_metadata.joblib"
OUTPUT_DIR = "outputs"

def load_and_filter(file_path):
    df = pd.read_csv(file_path)
    df.columns = [c.lower().strip().replace('"', '') for c in df.columns]

    if "tagname" in df.columns:
        df.rename(columns={"tagname": "skill_abr"}, inplace=True)
    if "count" in df.columns:
        df.rename(columns={"count": "skill_count"}, inplace=True)

    df["date"] = pd.to_datetime(df["date"].astype(str).str.replace('"', '').str.strip())
    df["skill_abr"] = df["skill_abr"].astype(str).str.replace('"', '').str.strip().str.lower()
    df["skill_count"] = df["skill_count"].astype(str).str.replace('"', '').str.strip().astype(int)

    # 1. Drop months with insufficient total counts (drops incomplete/sparse scrapes)
    monthly_volumes = df.groupby("date")["skill_count"].sum()
    median_vol = monthly_volumes.median()
    valid_dates = monthly_volumes[monthly_volumes >= (0.35 * median_vol)].index
    df = df[df["date"].isin(valid_dates)].copy()

    # 2. Compute Market Share (%)
    totals = df.groupby("date")["skill_count"].transform("sum")
    df["skill_share"] = (df["skill_count"] / totals.replace(0, 1)) * 100

    return df

def forecast_skill(skill_name, periods_ahead=6):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model = joblib.load(MODEL_FILE)
    meta = joblib.load(METADATA_FILE)

    skill_clean = skill_name.strip().lower()
    if skill_clean not in meta["available_skills"]:
        raise ValueError(f"Skill '{skill_name}' not recognized. Available: {meta['available_skills']}")

    raw_df = load_and_filter(DATA_FILE)
    series = raw_df[raw_df["skill_abr"] == skill_clean].sort_values("date").copy()

    history = series["skill_share"].tolist()
    last_date = series["date"].max()

    future_dates = []
    future_preds = []

    # Iterative multi-step prediction loop
    for step in range(1, periods_ahead + 1):
        target_date = last_date + pd.DateOffset(months=step)

        row = {
            "skill_cat": pd.Categorical([skill_clean], categories=meta["categories"]),
            "lag_share_1": [history[-1]],
            "lag_share_2": [history[-2]],
            "lag_share_3": [history[-3]],
            "momentum_1_3": [history[-1] - history[-3]],
            "rolling_share_3m": [np.mean(history[-3:])]
        }
        X = pd.DataFrame(row)[meta["features"]]
        pred = max(0.1, float(model.predict(X)[0]))

        history.append(pred)
        future_dates.append(target_date)
        future_preds.append(round(pred, 2))

    # Baseline: 3-month trailing average (avoids single-month outlier noise)
    baseline_3m = np.mean(series["skill_share"].iloc[-3:])
    end_val = future_preds[-1]
    diff = end_val - baseline_3m

    # Trend thresholds relative to moving baseline
    if diff > 0.4:
        trend = "GROWING"
    elif diff < -0.4:
        trend = "DECLINING"
    else:
        trend = "STABLE"

    print(f"\n==========================================")
    print(f" Demand Share Projection: {skill_clean.upper()} ({trend})")
    print(f" Last Closed Month: {last_date.strftime('%Y-%m')}")
    print(f" Trailing 3M Baseline: {baseline_3m:.2f}%")
    print(f" Projected Final Share: {end_val:.2f}% (Change: {diff:+.2f}%)")
    print(f"==========================================")

    # Plotting
    plt.figure(figsize=(10, 4.5))
    plot_df = series.tail(18)
    
    # Historical observations
    plt.plot(plot_df["date"], plot_df["skill_share"], label="Historical Share (%)", color="#1f77b4", marker="o")
    
    # Connect last actual point to the first forecast point
    connect_dates = [plot_df["date"].iloc[-1]] + future_dates
    connect_vals = [plot_df["skill_share"].iloc[-1]] + future_preds
    
    plt.plot(connect_dates, connect_vals, label=f"Forecasted Share ({trend})", color="#d62728", linestyle="--", marker="s")
    
    plt.title(f"Market Share Projection: {skill_clean.upper()} ({trend})")
    plt.xlabel("Timeline")
    plt.ylabel("% of Total Tech Market / Inquiries")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    safe_name = skill_clean.replace(".", "_").replace("/", "_")
    output_path = f"{OUTPUT_DIR}/{safe_name}_share_forecast.png"
    plt.savefig(output_path)
    print(f"Chart saved to: {output_path}")

if __name__ == "__main__":
    for s in ["python", "docker", "reactjs", "kubernetes"]:
        try:
            forecast_skill(s, periods_ahead=6)
        except Exception as e:
            print(f"Could not forecast {s}: {e}")