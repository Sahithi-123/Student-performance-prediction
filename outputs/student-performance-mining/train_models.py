from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

ROOT = Path(__file__).resolve().parent
out = ROOT / "models"
out.mkdir(exist_ok=True)
for filename, subject in [("student-mat.csv", "mathematics"), ("student-por.csv", "portuguese")]:
    df = pd.read_csv(ROOT / "data" / filename, sep=";")
    for scenario, exclude_grades in [("early_warning_no_G1_G2", True), ("in_year_with_G1_G2", False)]:
        X = df.drop(columns=["G3"] + (["G1", "G2"] if exclude_grades else []))
        y = pd.to_numeric(df["G3"])
        num = X.select_dtypes(include="number").columns.tolist()
        cat = [c for c in X.columns if c not in num]
        prep = ColumnTransformer([("num", "passthrough", num), ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
        model = Pipeline([("preprocess", prep), ("model", RandomForestRegressor(n_estimators=400, min_samples_leaf=2, random_state=42, n_jobs=-1))])
        model.fit(X, y)
        joblib.dump(model, out / f"{subject}_{scenario}.joblib")
print(f"Saved four demo prediction models in {out}")
