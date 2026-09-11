# data_prep.py
import os
import re
import pandas as pd
import numpy as np
import kagglehub

OUTPUT_DIR = "data"
PROCESSED_FILE = os.path.join(OUTPUT_DIR, "weekly_skill_panel.csv")

# Regular expression mappings covering your exact skill inventory
SKILL_PATTERNS = {
    "Python": r"\bpython\b",
    "Java": r"\bjava\b(?!script)",
    "SQL": r"\bsql\b",
    "Machine Learning": r"\bmachine\s+learning|\bml\b",
    "Deep Learning": r"\bdeep\s+learning|\bdl\b",
    "MLOps": r"\bmlops\b",
    "LLMs": r"\bllms?|\blarge\s+language\s+models?\b",
    "RAG": r"\brag\b|\bretrieval[\s-]augmented\b",
    "Vector Databases": r"\bvector\s+dbs?|\bvector\s+databases?\b|\bpinecone|\bweaviate|\bchroma\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\b(kubernetes|k8s)\b",
    "React": r"\breact(\.js|js)?\b",
    "Node.js": r"\bnode(\.js|js)?\b",
    "Spring Boot": r"\bspring\s*boot\b",
    "AWS": r"\baws\b|\bamazon\s+web\s+services\b",
    "Flutter": r"\bflutter\b",
    "Solidity": r"\bsolidity\b",
    "OpenCV": r"\bopencv\b",
    "CI/CD": r"\bci[\/-]?cd\b"
}

def find_file(root_dir, target_name):
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.lower() == target_name.lower():
                return os.path.join(root, f)
    return None

def process_sede_or_kaggle():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Check if user already placed SEDE query result in data/
    if os.path.exists(PROCESSED_FILE):
        df_check = pd.read_csv(PROCESSED_FILE, nrows=5)
        cols = [c.lower() for c in df_check.columns]
        if "date" in cols and any(s in cols for s in ["skill_abr", "tagname"]) and any(c in cols for c in ["skill_count", "count"]):
            print(f"Detected pre-existing SEDE dataset in {PROCESSED_FILE}.")
            df = pd.read_csv(PROCESSED_FILE)
            # Standardize column headers
            col_map = {c: c.lower() for c in df.columns}
            df.rename(columns=col_map, inplace=True)
            if "tagname" in df.columns:
                df.rename(columns={"tagname": "skill_abr"}, inplace=True)
            if "count" in df.columns:
                df.rename(columns={"count": "skill_count"}, inplace=True)
            
            df["date"] = pd.to_datetime(df["date"])
            df["skill_abr"] = df["skill_abr"].str.strip().str.title()
            df = df.sort_values(["skill_abr", "date"]).reset_index(drop=True)
            df.to_csv(PROCESSED_FILE, index=False)
            print(f"Validated and formatted {len(df)} rows across {df['skill_abr'].nunique()} skills.")
            return

    # 2. Fallback to Kaggle LinkedIn Archive
    print("SEDE CSV not detected in data/. Downloading/locating Kaggle dataset via kagglehub...")
    raw_path = kagglehub.dataset_download("arshkon/linkedin-job-postings")
    postings_path = find_file(raw_path, "postings.csv")
    
    if not postings_path:
        raise FileNotFoundError(f"Could not find 'postings.csv' in {raw_path}")

    print(f"Parsing postings from: {postings_path}")
    compiled = {k: re.compile(v, re.IGNORECASE) for k, v in SKILL_PATTERNS.items()}
    collected_chunks = []

    # Stream large CSV in chunks
    for chunk in pd.read_csv(postings_path, usecols=["original_listed_time", "description"], chunksize=20000, low_memory=False):
        chunk["date"] = pd.to_datetime(chunk["original_listed_time"], unit="ms", errors="coerce")
        chunk = chunk.dropna(subset=["date"])
        if chunk.empty:
            continue
            
        desc = chunk["description"].fillna("").astype(str)
        for skill_name, pat in compiled.items():
            flags = desc.str.contains(pat, regex=True).astype(int)
            grouped = chunk.assign(hit=flags).groupby(pd.Grouper(key="date", freq="W"))["hit"].sum().reset_index()
            grouped["skill_abr"] = skill_name
            grouped.rename(columns={"hit": "skill_count"}, inplace=True)
            collected_chunks.append(grouped)

    combined = pd.concat(collected_chunks, ignore_index=True)
    panel = combined.groupby(["date", "skill_abr"])["skill_count"].sum().reset_index()
    
    # Fill sparse weeks
    all_dates = panel["date"].unique()
    grid_idx = pd.MultiIndex.from_product([all_dates, list(SKILL_PATTERNS.keys())], names=["date", "skill_abr"])
    panel = panel.set_index(["date", "skill_abr"]).reindex(grid_idx, fill_value=0).reset_index()
    
    panel.to_csv(PROCESSED_FILE, index=False)
    print(f"Successfully generated panel with {len(panel)} rows at {PROCESSED_FILE}")

if __name__ == "__main__":
    process_sede_or_kaggle()