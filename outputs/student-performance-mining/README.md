# Student performance prediction with data mining

An educational, reproducible project based on Cortez and Silva (2008), using the supplied UCI student records for Mathematics and Portuguese. It predicts the final-period grade (`G3`) and compares an early-warning setup with a later in-year setup.

## Research question

How well can student final grades and pass/fail outcomes be predicted from demographic, family, school, study and lifestyle variables, and how much does performance change when first- and second-period grades (`G1`, `G2`) become available?

## Data

The `data/` directory contains the supplied, semicolon-delimited files. Mathematics has 395 records and Portuguese has 649. The target is `G3` on a 0–20 scale. This is observational data from two Portuguese secondary schools in 2005–2006; it does not establish causal effects or generalize automatically to other schools or cohorts.

`student.txt` defines the variables. The supplied `student-merge.R` joins on 13 shared attributes, which are not unique identifiers. Multiple matches can therefore occur and the resulting 382-row count should not be interpreted as 382 verified individual matches. This project analyzes each subject separately, avoiding that uncertain linkage.

## Method

The script performs a reproducible 75/25 random train/test split (seed 42) separately for each subject and input scenario. It one-hot encodes categorical variables within a scikit-learn pipeline, then evaluates a shallow decision tree and random forest for regression and pass/fail classification. Pass is defined as `G3 >= 10`. Regression reports MAE, RMSE and R²; classification reports accuracy and macro-F1. Random-forest impurity importance is exported as a descriptive ranking, not a causal explanation.

- **Early warning:** excludes `G1` and `G2` to represent prediction before period grades are available.
- **In-year update:** includes `G1` and `G2`, which are strong signals but make the prediction less early.

This is a compact classroom reproduction, not an exact replication of the paper's 20 repetitions of 10-fold cross-validation or its four algorithms. It also does not implement the paper's five-level classification task.

## Run

Install Python 3.10+ and dependencies:

```bash
python -m pip install -r requirements.txt
python student_performance.py
```

Optional paths:

```bash
python student_performance.py --data-dir ./data --output-dir ./results
```

Outputs are `results/data_summary.csv`, `results/model_metrics.csv` and `results/feature_importance.csv`. Repeated runs with the same data and package versions use the same split and seed.

## Launch the web app

Install the same dependencies, then from this project folder run:

```bash
python train_models.py
streamlit run app.py
```

Streamlit opens the dashboard in your browser. The dashboard compares model results, displays feature importance, and includes an Early Support Explorer. Enter sex, age, school, absences, past failures, G1 and G2 to compare estimates before and after period grades become available. Other model fields are filled with typical values from that subject's dataset. The training step creates local model files under `models/`.

## Interpret results responsibly

Use the early-warning scores to assess how useful non-grade indicators might be for identifying students for supportive follow-up. Use the in-year scores as a benchmark for a later update. Neither predicts an individual with certainty. Avoid treating demographic or social variables as grounds for punitive decisions; predictions should prompt respectful human review and access to support. The data contain no identifiers but can still encode unfair associations.

## Sources

- Cortez, P. & Silva, A. M. G. (2008). *Using data mining to predict secondary school student performance*. Proceedings of the 5th Annual Future Business Technology Conference. [Paper PDF](https://citeseerx.ist.psu.edu/document?doi=61d468d5254730bbecf822c6b60d7d6595d9889c&repid=rep1&type=pdf).
- Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning Repository. [Dataset record](https://archive.ics.uci.edu/dataset/320/student%2Bperformance). DOI: 10.24432/C5TG7T.
