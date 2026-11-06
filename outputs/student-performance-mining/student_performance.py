"""Reproducible analysis of the UCI Student Performance data."""
from pathlib import Path
import argparse

try:
    import pandas as pd  # pyright: ignore[reportMissingModuleSource, reportMissingImports]
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: pandas is required. Install it with: "
        "python -m pip install pandas"
    ) from exc

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

ROOT = Path(__file__).resolve().parent
TARGET = "G3"
GRADE_INPUTS = {"G1", "G2"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, importances, summaries = [], [], []
    for filename, subject in [("student-mat.csv", "Mathematics"), ("student-por.csv", "Portuguese")]:
        df = pd.read_csv(args.data_dir / filename, sep=";")
        df["G3"] = pd.to_numeric(df["G3"])
        summaries.append({"subject": subject, "students": len(df), "columns": len(df.columns),
                          "missing_cells": int(df.isna().sum().sum()), "duplicate_rows": int(df.duplicated().sum()),
                          "mean_G3": round(df.G3.mean(), 3), "median_G3": round(df.G3.median(), 3),
                          "pass_rate_G3_ge_10": round((df.G3 >= 10).mean(), 3)})
        for scenario, drop_grades in [("early_warning_no_G1_G2", True), ("in_year_with_G1_G2", False)]:
            X = df.drop(columns=[TARGET] + (list(GRADE_INPUTS) if drop_grades else []))
            y = df[TARGET]
            numeric = X.select_dtypes(include="number").columns.tolist()
            categorical = [c for c in X.columns if c not in numeric]
            prep = ColumnTransformer([("num", "passthrough", numeric),
                                      ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)])
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=42)
            for name, estimator in [("DecisionTree", DecisionTreeRegressor(max_depth=5, random_state=42)),
                                    ("RandomForest", RandomForestRegressor(n_estimators=400, min_samples_leaf=2, random_state=42, n_jobs=-1))]:
                model = Pipeline([("preprocess", prep), ("model", estimator)])
                model.fit(X_train, y_train)
                pred = model.predict(X_test)
                rows.append({"subject": subject, "scenario": scenario, "task": "regression", "model": name,
                             "MAE": round(mean_absolute_error(y_test, pred), 3),
                             "RMSE": round(mean_squared_error(y_test, pred) ** .5, 3),
                             "R2": round(r2_score(y_test, pred), 3), "accuracy": "", "macro_F1": ""})
                if name == "RandomForest":
                    names = model.named_steps["preprocess"].get_feature_names_out()
                    for feature, score in zip(names, model.named_steps["model"].feature_importances_):
                        importances.append({"subject": subject, "scenario": scenario, "feature": feature, "importance": score})
            # Binary pass/fail classification, aligned with the paper's pass/fail task.
            y_class = (df[TARGET] >= 10).astype(int)
            yc_train, yc_test = y_class.loc[X_train.index], y_class.loc[X_test.index]
            for name, estimator in [("DecisionTree", DecisionTreeClassifier(max_depth=5, random_state=42, class_weight="balanced")),
                                    ("RandomForest", RandomForestClassifier(n_estimators=400, min_samples_leaf=2, random_state=42, n_jobs=-1, class_weight="balanced"))]:
                model = Pipeline([("preprocess", prep), ("model", estimator)])
                model.fit(X_train, yc_train)
                pred = model.predict(X_test)
                rows.append({"subject": subject, "scenario": scenario, "task": "pass_fail", "model": name,
                             "MAE": "", "RMSE": "", "R2": "", "accuracy": round(accuracy_score(yc_test, pred), 3),
                             "macro_F1": round(f1_score(yc_test, pred, average="macro"), 3)})
    pd.DataFrame(summaries).to_csv(args.output_dir / "data_summary.csv", index=False)
    pd.DataFrame(rows).to_csv(args.output_dir / "model_metrics.csv", index=False)
    imp = pd.DataFrame(importances)
    imp["feature"] = imp["feature"].str.replace(r"^(num|cat)__", "", regex=True)
    imp = imp.groupby(["subject", "scenario", "feature"], as_index=False)["importance"].sum()
    imp = imp.sort_values(["subject", "scenario", "importance"], ascending=[True, True, False])
    imp.to_csv(args.output_dir / "feature_importance.csv", index=False)
    print("Wrote data_summary.csv, model_metrics.csv, and feature_importance.csv to", args.output_dir)

if __name__ == "__main__":
    main()
