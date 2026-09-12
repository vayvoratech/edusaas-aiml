import os
from pathlib import Path
import joblib


class FraudModelLoader:
    """
    Load trained Fraud Detection models with dynamic multi-candidate path resolution.
    """

    def __init__(self, model_dir="models/fraud"):
        current_dir = Path(__file__).resolve().parent

        # ==================================================
        # 1. CANDIDATE BASE DIRECTORIES
        # ==================================================
        dir_candidates = [
            current_dir.parent.parent / "models" / "fraud",  # Root models/fraud/
            Path("/app/models/fraud"),                       # Container /app/models/fraud/
            Path("models/fraud"),                            # CWD models/fraud/
            current_dir / "models" / "fraud",                # Module local models/fraud/
            current_dir / "models",                          # Module local models/
            Path(model_dir),                                 # Explicit path argument
        ]

        # Select the first directory candidate that exists on disk
        self.base_dir = next((d for d in dir_candidates if d.is_dir()), dir_candidates[0])

        # ==================================================
        # 2. RESOLVE INDIVIDUAL ARTIFACT PATHS
        # ==================================================
        self.rf_path = self._resolve_file("fraud_random_forest.pkl")
        self.iso_path = self._resolve_file("fraud_isolation_forest.pkl")
        self.features_path = self._resolve_file("fraud_feature_columns.pkl")

        self.random_forest_model = None
        self.isolation_forest_model = None
        self.feature_columns = None
        self.last_load_error = None

        print("\n" + "=" * 55)
        print("FRAUD MODEL LOADER: PATH RESOLUTION")
        print("=" * 55)
        print(f"Base Directory   : {self.base_dir}")
        print(f"Random Forest    : {self.rf_path} (exists: {self.rf_path.is_file()})")
        print(f"Isolation Forest : {self.iso_path} (exists: {self.iso_path.is_file()})")
        print(f"Feature Columns  : {self.features_path} (exists: {self.features_path.is_file()})")
        print("=" * 55 + "\n")

        self.load_models()

    def _resolve_file(self, filename: str) -> Path:
        """Finds file in base directory or system root candidates."""
        current_dir = Path(__file__).resolve().parent
        candidates = [
            self.base_dir / filename,
            current_dir.parent.parent / "models" / filename,
            Path(f"/app/models/{filename}"),
            Path(f"models/{filename}"),
            current_dir / filename,
        ]
        return next((p for p in candidates if p.is_file()), candidates[0])

    def load_models(self):
        """Loads serialized models with fail-safe error handling."""
        missing = []
        if not self.rf_path.is_file():
            missing.append(str(self.rf_path))
        if not self.iso_path.is_file():
            missing.append(str(self.iso_path))
        if not self.features_path.is_file():
            missing.append(str(self.features_path))

        if missing:
            self.last_load_error = f"Missing artifact files: {', '.join(missing)}"
            print(f"[FraudModelLoader ERROR] {self.last_load_error}")
            return

        try:
            self.random_forest_model = joblib.load(str(self.rf_path))
            self.isolation_forest_model = joblib.load(str(self.iso_path))
            self.feature_columns = joblib.load(str(self.features_path))
            print("Fraud Models Loaded Successfully.")
        except Exception as e:
            self.last_load_error = f"joblib unpickling failed: {type(e).__name__}: {e}"
            print(f"[FraudModelLoader ERROR] {self.last_load_error}")


fraud_model_loader = FraudModelLoader()