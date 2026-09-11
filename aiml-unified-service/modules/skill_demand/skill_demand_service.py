# modules/skill_demand/skill_demand_service.py
import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt


class SkillDemandService:

    def __init__(
        self,
        data_file="weekly_skill_panel.csv",
        model_file="skill_lgbm_model.joblib",
        metadata_file="model_metadata.joblib",
        output_dir="outputs"
    ):
        current_dir = Path(__file__).resolve().parent

        # ==================================================
        # 1. MODEL PATH RESOLUTION
        # ==================================================
        model_candidates = [
            current_dir.parent.parent / "models" / "skill_lgbm_model.joblib",   # root models/
            Path("/app/models/skill_lgbm_model.joblib"),                         # container root
            Path("models/skill_lgbm_model.joblib"),                              # cwd models/
            current_dir / "models" / "skill_lgbm_model.joblib",                  # module local: modules/skill_demand/models/
            Path(model_file),                                                    # explicit argument
        ]
        self.model_file = next((p for p in model_candidates if p.is_file()), model_candidates[0])

        # ==================================================
        # 2. METADATA PATH RESOLUTION
        # ==================================================
        meta_candidates = [
            current_dir.parent.parent / "models" / "model_metadata.joblib",     # root models/
            Path("/app/models/model_metadata.joblib"),                           # container root
            Path("models/model_metadata.joblib"),                                # cwd models/
            current_dir / "models" / "model_metadata.joblib",                    # module local: modules/skill_demand/models/
            Path(metadata_file),                                                 # explicit argument
        ]
        self.metadata_file = next((p for p in meta_candidates if p.is_file()), meta_candidates[0])

        # ==================================================
        # 3. DATASET PATH RESOLUTION (data inside models/)
        # ==================================================
        data_candidates = [
            current_dir.parent.parent / "models" / "data" / "weekly_skill_panel.csv",  # root models/data/
            Path("/app/models/data/weekly_skill_panel.csv"),                            # container root /app/models/data/
            Path("models/data/weekly_skill_panel.csv"),                                 # cwd models/data/
            current_dir / "models" / "data" / "weekly_skill_panel.csv",                 # module local: modules/skill_demand/models/data/
            current_dir.parent.parent / "data" / "weekly_skill_panel.csv",              # fallback root data/
            Path(data_file),                                                             # explicit argument
        ]
        self.data_file = next((p for p in data_candidates if p.is_file()), data_candidates[0])

        # ==================================================
        # 4. OUTPUT DIRECTORY RESOLUTION
        # ==================================================
        self.output_dir = current_dir / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.meta = None
        self.raw_df = None
        self.last_load_error = None

        print("\n" + "=" * 55)
        print("SKILL DEMAND ENGINE: PATH CANDIDATE RESOLUTION")
        print("=" * 55)
        print(f"Model file   : {self.model_file} (exists: {self.model_file.is_file()})")
        print(f"Metadata file: {self.metadata_file} (exists: {self.metadata_file.is_file()})")
        print(f"Dataset file : {self.data_file} (exists: {self.data_file.is_file()})")
        print(f"Output dir   : {self.output_dir}")
        print("=" * 55 + "\n")

        self.load_artifacts()
        self.load_panel_data()

    def load_artifacts(self):
        """Loads serialized model and metadata with size validation."""
        if not self.model_file.is_file():
            self.last_load_error = f"Model artifact not found on disk at {self.model_file}"
            print(f"[SkillDemand ERROR] {self.last_load_error}")
            return
        if not self.metadata_file.is_file():
            self.last_load_error = f"Metadata artifact not found on disk at {self.metadata_file}"
            print(f"[SkillDemand ERROR] {self.last_load_error}")
            return

        model_size = self.model_file.stat().st_size
        meta_size = self.metadata_file.stat().st_size
        print(f"[SkillDemand] Discovered model: {self.model_file} ({model_size} bytes)")
        print(f"[SkillDemand] Discovered metadata: {self.metadata_file} ({meta_size} bytes)")

        # Git LFS pointer text file is typically ~120-140 bytes
        if model_size < 500:
            self.last_load_error = (
                f"Model file at {self.model_file} is only {model_size} bytes. "
                "This is a Git LFS pointer text file, not the raw binary weights!"
            )
            print(f"[SkillDemand CRITICAL] {self.last_load_error}")
            return

        try:
            self.model = joblib.load(str(self.model_file))
            self.meta = joblib.load(str(self.metadata_file))
            print("[SkillDemand] Successfully loaded LightGBM model and metadata.")
        except Exception as e:
            self.last_load_error = f"joblib.load unpickling error: {type(e).__name__}: {str(e)}"
            print(f"[SkillDemand ERROR] {self.last_load_error}")

    def load_panel_data(self):
        """Cleans and normalizes weekly panel into percentage market share."""
        if not self.data_file.is_file():
            print(f"[SkillDemand ERROR] Missing dataset file at: {self.data_file}")
            return

        try:
            df = pd.read_csv(str(self.data_file))
            df.columns = [c.lower().strip().replace('"', '') for c in df.columns]

            if "tagname" in df.columns:
                df.rename(columns={"tagname": "skill_abr"}, inplace=True)
            if "count" in df.columns:
                df.rename(columns={"count": "skill_count"}, inplace=True)

            df["date"] = pd.to_datetime(df["date"].astype(str).str.replace('"', '').str.strip())
            df["skill_abr"] = df["skill_abr"].astype(str).str.replace('"', '').str.strip().str.lower()
            df["skill_count"] = df["skill_count"].astype(str).str.replace('"', '').str.strip().astype(int)

            # Filter out low-volume boundary periods
            monthly_volumes = df.groupby("date")["skill_count"].sum()
            median_vol = monthly_volumes.median()
            valid_dates = monthly_volumes[monthly_volumes >= (0.35 * median_vol)].index
            df = df[df["date"].isin(valid_dates)].copy()

            # Compute market share %
            totals = df.groupby("date")["skill_count"].transform("sum")
            df["skill_share"] = (df["skill_count"] / totals.replace(0, 1)) * 100
            self.raw_df = df
            print(f"[SkillDemand] Dataset loaded successfully ({len(df)} rows).")
        except Exception as e:
            print(f"[SkillDemand ERROR] Failed to load dataset: {type(e).__name__}: {e}")

    def get_available_skills(self) -> list:
        if not self.meta:
            return []
        return self.meta.get("available_skills", [])

    def forecast_skill(self, skill_name: str, periods: int = 6) -> dict:
        if self.model is None or self.meta is None or self.raw_df is None:
            missing = []
            if self.model is None: missing.append(f"Model ({self.model_file})")
            if self.meta is None: missing.append(f"Metadata ({self.metadata_file})")
            if self.raw_df is None: missing.append(f"Dataset ({self.data_file})")

            error_diag = self.last_load_error or "Artifacts missing on disk or failed unpickling."
            raise RuntimeError(f"Missing loaded artifacts: {', '.join(missing)} | Details: {error_diag}")

        skill_clean = skill_name.strip().lower()
        if skill_clean not in self.meta["available_skills"]:
            raise ValueError(f"Skill '{skill_name}' not recognized. Available: {self.meta['available_skills']}")

        series = self.raw_df[self.raw_df["skill_abr"] == skill_clean].sort_values("date").copy()
        if series.empty or len(series) < 3:
            raise ValueError(f"Insufficient historical records for '{skill_name}'.")

        history = series["skill_share"].tolist()
        last_date = series["date"].max()

        future_dates = []
        future_preds = []

        # Recursive autoregressive inference loop
        for step in range(1, periods + 1):
            target_date = last_date + pd.DateOffset(months=step)
            row = {
                "skill_cat": pd.Categorical([skill_clean], categories=self.meta["categories"]),
                "lag_share_1": [history[-1]],
                "lag_share_2": [history[-2]],
                "lag_share_3": [history[-3]],
                "momentum_1_3": [history[-1] - history[-3]],
                "rolling_share_3m": [np.mean(history[-3:])]
            }
            X = pd.DataFrame(row)[self.meta["features"]]
            pred = max(0.1, float(self.model.predict(X)[0]))

            history.append(pred)
            future_dates.append(target_date)
            future_preds.append(round(pred, 2))

        baseline_3m = float(np.mean(series["skill_share"].iloc[-3:]))
        end_val = future_preds[-1]
        diff = round(end_val - baseline_3m, 2)

        if diff > 0.4:
            trend = "GROWING"
        elif diff < -0.4:
            trend = "DECLINING"
        else:
            trend = "STABLE"

        # Generate & save plot
        safe_name = skill_clean.replace(".", "_").replace("/", "_")
        output_filename = f"{safe_name}_share_forecast.png"
        output_path = self.output_dir / output_filename

        plot_df = series.tail(18)
        plt.figure(figsize=(10, 4.5))
        plt.plot(plot_df["date"], plot_df["skill_share"], label="Historical Share (%)", color="#1f77b4", marker="o")

        connect_dates = [plot_df["date"].iloc[-1]] + future_dates
        connect_vals = [plot_df["skill_share"].iloc[-1]] + future_preds
        plt.plot(connect_dates, connect_vals, label=f"Forecasted Share ({trend})", color="#d62728", linestyle="--", marker="s")

        plt.title(f"Market Share Projection: {skill_clean.upper()} ({trend})")
        plt.xlabel("Timeline")
        plt.ylabel("% of Total Tech Inquiries")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(str(output_path))
        plt.close()

        return {
            "skill": skill_clean,
            "trend": trend,
            "last_observed_date": last_date.strftime("%Y-%m-%d"),
            "trailing_3m_baseline_pct": round(baseline_3m, 2),
            "final_projected_share_pct": end_val,
            "net_share_change_pct": diff,
            "saved_chart_path": str(output_path),
            "chart_url": f"/outputs/{output_filename}",
            "timeline": [
                {"date": d.strftime("%Y-%m-%d"), "predicted_share_pct": p}
                for d, p in zip(future_dates, future_preds)
            ]
        }