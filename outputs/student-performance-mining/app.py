from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Student Performance Lab", page_icon="📘", layout="wide")
st.markdown("""<style>
.stApp{background:var(--background-color);color:var(--text-color)}
.block-container{max-width:1180px;padding-top:2rem}
.hero{background:linear-gradient(120deg,#172b4d,#246b78);padding:28px 34px;border-radius:18px;color:#fff;margin-bottom:20px}
.hero h1{color:#fff!important;margin:0}.hero p{color:#e3eef4!important;margin:8px 0 0}
[data-testid="stCaptionContainer"],.stMarkdown p{color:var(--text-color)}
[data-testid="stDataFrame"]{color:var(--text-color)}
</style>""", unsafe_allow_html=True)
st.markdown("<div class='hero'><h1>Student Performance Lab</h1><p>Explore what school records can tell us about final grades — and what they cannot.</p></div>", unsafe_allow_html=True)

metrics = pd.read_csv(ROOT / "results" / "model_metrics.csv")
summary = pd.read_csv(ROOT / "results" / "data_summary.csv")
importance = pd.read_csv(ROOT / "results" / "feature_importance.csv")
subject = st.selectbox("Subject", ["Mathematics", "Portuguese"])
scenario = st.radio("Prediction timing", ["early_warning_no_G1_G2", "in_year_with_G1_G2"], horizontal=True,
                    index=1,
                    format_func=lambda x: "Early warning · before period grades" if x.startswith("early") else "In-year update · G1 and G2 available")
s = summary[summary.subject == subject].iloc[0]
cols = st.columns(4)
for col, label, value in zip(cols, ["Students", "Average final grade", "Pass rate (G3 ≥ 10)", "Missing values"],
                              [int(s.students), f"{s.mean_G3:.1f} / 20", f"{s.pass_rate_G3_ge_10:.0%}", int(s.missing_cells)]):
    col.metric(label, value)
st.divider()
left, right = st.columns([1.2, 1])
with left:
    st.subheader("Model comparison")
    view = metrics[(metrics.subject == subject) & (metrics.scenario == scenario)].copy()
    view["model_task"] = view.model + " · " + view.task.str.replace("_", " ").str.title()
    st.dataframe(view[["model_task", "MAE", "RMSE", "R2", "accuracy", "macro_F1"]].set_index("model_task"), use_container_width=True)
    st.caption("Lower MAE/RMSE and higher R² are better for regression. Classification reports accuracy and macro-F1.")
with right:
    st.subheader("Top model signals")
    top = importance[(importance.subject == subject) & (importance.scenario == scenario)].head(8)
    st.bar_chart(top.set_index("feature")["importance"].sort_values(), color="#287b83")

st.divider()
st.subheader("Early support explorer")
st.write("Compare what the model estimates before period grades are available with its estimate after G1 and G2 arrive.")
raw = pd.read_csv(ROOT / "data" / ("student-mat.csv" if subject == "Mathematics" else "student-por.csv"), sep=";")
model_dir = ROOT / "models"
early_path = model_dir / f"{subject.lower()}_early_warning_no_G1_G2.joblib"
year_path = model_dir / f"{subject.lower()}_in_year_with_G1_G2.joblib"
if not early_path.exists() or not year_path.exists():
    st.warning("Prediction models are not saved yet. In the project folder, run: python train_models.py")
else:
    import joblib
    early_model, year_model = joblib.load(early_path), joblib.load(year_path)
    with st.form("support_explorer"):
        st.markdown("**Student details**")
        c1, c2, c3 = st.columns(3)
        sex = c1.selectbox("Sex", sorted(raw.sex.dropna().unique().tolist()))
        age = c2.slider("Age", int(raw.age.min()), int(raw.age.max()), int(raw.age.median()))
        school = c3.selectbox("School", sorted(raw.school.dropna().unique().tolist()))
        c4, c5, c6 = st.columns(3)
        absences = c4.slider("Absences", int(raw.absences.min()), int(raw.absences.max()), int(raw.absences.median()))
        failures = c5.slider("Past class failures", int(raw.failures.min()), int(raw.failures.max()), int(raw.failures.median()))
        g1 = c6.slider("G1 score", 0, 20, int(raw.G1.median()))
        g2 = st.slider("G2 score", 0, 20, int(raw.G2.median()))
        submitted = st.form_submit_button("Compare prediction stages")
    st.caption("Other model fields use typical values from the selected subject dataset. Adjust the inputs and submit again to explore how the model responds.")
    if submitted:
        base = {}
        for col in raw.columns:
            if col == "G3":
                continue
            if col in {"sex", "age", "school", "absences", "failures", "G1", "G2"}:
                base[col] = {"sex": sex, "age": age, "school": school, "absences": absences,
                             "failures": failures, "G1": g1, "G2": g2}[col]
            elif pd.api.types.is_numeric_dtype(raw[col]):
                base[col] = raw[col].median()
            else:
                mode = raw[col].mode(dropna=True)
                base[col] = mode.iloc[0] if not mode.empty else raw[col].iloc[0]
        early_input = pd.DataFrame([{k: v for k, v in base.items() if k not in {"G1", "G2"}}])
        year_input = pd.DataFrame([base])
        early_grade = float(early_model.predict(early_input)[0])
        year_grade = float(year_model.predict(year_input)[0])
        a, b = st.columns(2)
        a.metric("Before G1 and G2", f"{early_grade:.1f} / 20")
        b.metric("After G1 and G2", f"{year_grade:.1f} / 20", f"{year_grade - early_grade:+.1f} points")
        average = float(s.mean_G3)
        st.write(f"Dataset average for {subject}: **{average:.1f} / 20**. The estimates are shown for context; neither one is a judgment of a student's ability.")
        if min(early_grade, year_grade) < 10:
            st.info("A lower estimate can be a reason to check whether practical academic support would be useful.")
        else:
            st.info("The estimates are a snapshot from this model. Keep offering support based on the student's own needs and goals.")
        st.caption("Changing an input shows how this fitted model responds. It does not prove that changing that factor would cause a grade to change.")

with st.expander("How to read this responsibly"):
    st.write("The records are from two Portuguese schools in 2005–2006. Predictions can be wrong and may not transfer to other schools. Use this demonstration to understand the research, not to make decisions about a real student's opportunities.")

st.markdown("### About this project\nBased on Cortez & Silva (2008), using historical records from two Portuguese schools. Associations are not causal and the model may not generalize to other schools.")
st.markdown("[Research paper](https://citeseerx.ist.psu.edu/document?doi=61d468d5254730bbecf822c6b60d7d6595d9889c&repid=rep1&type=pdf) · [UCI dataset](https://archive.ics.uci.edu/dataset/320/student%2Bperformance)")
