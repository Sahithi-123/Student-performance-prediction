from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

OUT = Path(r'C:\Users\USER\Documents\Codex\2026-11-01\corpus-id-16621299-using-data-mining\outputs\Student_Performance_Project_Report.docx')
doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(.7); sec.bottom_margin = Inches(.65); sec.left_margin = Inches(.8); sec.right_margin = Inches(.8)

styles = doc.styles
styles['Normal'].font.name = 'Aptos'; styles['Normal'].font.size = Pt(10); styles['Normal'].font.color.rgb = RGBColor(42, 51, 64)
styles['Normal'].paragraph_format.space_after = Pt(6)
for name, size in [('Title', 26), ('Heading 1', 17), ('Heading 2', 12)]:
    st = styles[name]; st.font.name='Aptos Display'; st.font.size=Pt(size); st.font.bold=True; st.font.color.rgb=RGBColor(0,0,0)
    st.paragraph_format.space_before=Pt(12 if name!='Title' else 0); st.paragraph_format.space_after=Pt(5)

def shade(cell, fill):
    pr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); pr.append(shd)
def set_cell(cell, text, bold=False, color='263548', size=8.5):
    cell.text=''; p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(2); p.paragraph_format.space_before=Pt(2)
    r=p.add_run(str(text)); r.bold=bold; r.font.name='Aptos'; r.font.size=Pt(size); r.font.color.rgb=RGBColor.from_string(color)
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
def table(headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.style='Table Grid'
    for i,h in enumerate(headers): set_cell(t.rows[0].cells[i],h,True,'FFFFFF',8.5); shade(t.rows[0].cells[i],'24465A')
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,v in enumerate(row):
            set_cell(cells[i],v,size=8.2)
            if ri%2==1: shade(cells[i],'EFF4F7')
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width= Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t
def para(text, style=None): doc.add_paragraph(text, style)
def bullet(text): doc.add_paragraph(text, style='List Bullet')

# Running header and footer
header=sec.header.paragraphs[0]; header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=header.add_run('STUDENT PERFORMANCE MINING  |  PROJECT REPORT'); r.font.size=Pt(8); r.font.color.rgb=RGBColor(90,105,119)
footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run('Student Performance Prediction Project'); r.font.size=Pt(8); r.font.color.rgb=RGBColor(110,120,130)

p=doc.add_paragraph(style='Title'); p.add_run('Student Performance Prediction')
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(12)
r=p.add_run('Project report · Data mining and interactive web application'); r.font.size=Pt(12); r.font.color.rgb=RGBColor(36,91,110)
para('This report explains a classroom data-mining project based on the student performance study by Cortez and Silva. It describes the research question, the two subject datasets, the modeling workflow, the interactive Streamlit app, the observed results, and the limits on interpreting predictions.')

doc.add_heading('Executive summary', level=1)
para('The project uses student records from Mathematics and Portuguese to estimate final-period grade G3 and classify students as passing or failing. It compares estimates made before period grades are available with updated estimates after G1 and G2 are recorded. The web app now makes that comparison directly in an Early Support Explorer, using six visible inputs: sex, age, school, absences, past class failures, and G1/G2 scores. This gives the demonstration a clear story about how prediction changes over the school year.')
para('Across the fixed test split, Random Forest regression was substantially more accurate when G1 and G2 were included. The explorer places both estimates side by side and shows the difference alongside the subject dataset average. Remaining model inputs are filled with typical dataset values. These results describe patterns in historical records; they do not establish causes or determine any student’s ability or future.')

doc.add_heading('1. Background and project purpose', level=1)
para('Cortez and Silva (2008) investigated whether data-mining methods could predict secondary-school achievement and identify useful signals in student records. Their study considered grades alongside demographic, family, school, study, and social variables for two core subjects. The project presented here takes that research as its foundation and creates a reproducible analysis plus a web interface for exploring the findings.')
doc.add_heading('Project objectives', level=2)
for x in ['Describe and validate the Mathematics and Portuguese datasets supplied with the project.','Compare final-grade regression and pass/fail classification models.','Measure how performance changes when first- and second-period grades are available.','Show model results and a demonstration prediction through a simple interactive web app.','Explain uncertainty, data limitations, and responsible use of student predictions.']: bullet(x)

doc.add_heading('2. Data used', level=1)
para('The project includes two semicolon-delimited CSV files. Each row represents one student in one subject, and each file contains 33 columns. The target variable G3 is the final-period grade on a 0–20 scale. G1 and G2 are the first- and second-period grades. Other fields cover school, age, sex, family background, study time, support, absences, and lifestyle indicators. The accompanying student.txt file provides variable definitions.')
table(['Subject file','Records','Columns','Mean G3','Median G3','Pass rate (G3 ≥ 10)','Missing cells'],[
['Mathematics',395,33,'10.415','11','67.1%','0'],['Portuguese',649,33,'11.906','12','84.6%','0']], [1.25,.8,.7,.8,.8,1.2,1.0])
para('These records describe students at two Portuguese secondary schools during 2005–2006. The two subject files overlap in some students, but the supplied R script links them using shared descriptive fields rather than a unique identifier. Such fields may not uniquely identify a person, so the count produced by that merge is not treated as a confirmed list of matched students. This project analyzes each subject independently.')

doc.add_heading('3. Modeling approach', level=1)
doc.add_heading('Prediction scenarios', level=2)
table(['Scenario','Inputs','Interpretation'],[
['Early warning','All predictors except G1 and G2','Represents an estimate before the current year’s period grades are available.'],
['In-year update','Predictors including G1 and G2','Represents an update after earlier period grades have been recorded.']], [1.25,2.0,3.25])
para('The target is never included among the model inputs. Categorical predictors are one-hot encoded inside a scikit-learn pipeline. This lets the models process text categories such as school, guardian, or job type consistently and helps keep preprocessing within the model workflow.')
doc.add_heading('Models and tasks', level=2)
para('The analysis evaluates a decision tree and a Random Forest for two tasks. Regression predicts numeric G3. Binary classification predicts pass when G3 is at least 10 and fail otherwise. The tree is limited to depth five for a compact, understandable comparison. The Random Forest uses 400 trees and a minimum leaf size of two. Classification models use class weighting to reduce the effect of unequal pass and fail counts.')
doc.add_heading('Evaluation design', level=2)
para('For each subject and scenario, records are divided into 75% training and 25% test data using a fixed random seed of 42. Models learn from the training subset and are scored on held-out records. Regression is summarized by mean absolute error (MAE), root mean squared error (RMSE), and R-squared (R²). Lower MAE and RMSE mean smaller typical errors; higher R² means more variation in grades is explained by the fitted model. Classification uses accuracy and macro-F1. Macro-F1 averages performance across pass and fail classes, so it is informative when one class is more common.')

doc.add_heading('4. Results', level=1)
para('The following table reports the Random Forest scores from the generated results. The fixed split gives a clear demonstration of the comparison, but a single split can vary by chance and should not be treated as a definitive estimate of future performance.')
table(['Subject','Timing','MAE','RMSE','R²','Accuracy','Macro-F1'],[
['Mathematics','Early warning','3.057','3.791','0.376','0.687','0.633'],
['Mathematics','In-year update','1.094','1.789','0.861','0.909','0.904'],
['Portuguese','Early warning','2.081','2.840','0.200','0.834','0.664'],
['Portuguese','In-year update','0.734','1.165','0.865','0.896','0.789']], [1.1,1.15,.65,.7,.55,.8,.8])
doc.add_heading('What the scores suggest', level=2)
para('Including G1 and G2 greatly improves numeric grade prediction in both subjects. For Mathematics, the Random Forest R² rises from 0.376 in the early-warning setup to 0.861 in the in-year setup. For Portuguese it rises from 0.200 to 0.865. This is consistent with the original paper’s observation that earlier grades are highly informative about later grades.')
para('For pass/fail classification, Mathematics accuracy rises from 0.687 to 0.909, while macro-F1 rises from 0.633 to 0.904. Portuguese accuracy changes from 0.834 to 0.896 and macro-F1 from 0.664 to 0.789. The early-warning Portuguese accuracy is already high in part because 84.6% of this dataset passes; accuracy alone can obscure performance on the less frequent failing group, which is why macro-F1 is also shown.')
doc.add_heading('Feature importance', level=2)
para('In the early-warning Random Forest, the largest impurity-based importance values are absences (0.194) and past failures (0.138) for Mathematics; and past failures (0.252) and absences (0.061) for Portuguese. These values reflect how the fitted forest used features to make its splits. They are not effect sizes, explanations of why a student achieved a grade, or proof that changing a feature would change an outcome. Importance rankings can shift with the sample and model.')

doc.add_heading('5. Web application', level=1)
para('The Streamlit interface in app.py presents subject-level record counts, average G3, pass rate, missing values, model metrics, and Random Forest feature-importance rankings. The prediction centerpiece is the Early Support Explorer. Visitors choose a subject and enter sex, age, school, absences, past failures, G1, and G2. The app creates two prediction rows from those answers and typical values for the remaining attributes. For the early estimate it excludes G1 and G2; for the updated estimate it includes them. It then shows both grades, their point difference, and the subject dataset average.')
para('This paired view illustrates the paper’s key timing question: how much predictive information becomes available after earlier period assessments? Visitors can adjust the inputs and rerun the comparison to explore how the fitted models respond. The app uses supportive language if an estimate is below 10 and includes an expandable note explaining the data’s age and scope. Changes in model output are demonstrations of prediction behavior, not evidence that changing an input would cause a grade change. The training script train_models.py fits the four Random Forest regression models on the full subject datasets and saves them under models/.')
doc.add_heading('How to run the web app', level=2)
para('Install Python 3.10 or later. Open a terminal in the student-performance-mining project directory and run:')
p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(.25); p.paragraph_format.space_after=Pt(2)
r=p.add_run('python -m pip install -r requirements.txt\npython train_models.py\nstreamlit run app.py'); r.font.name='Consolas'; r.font.size=Pt(9); r.font.color.rgb=RGBColor(36,91,110)
para('The first command installs the project dependencies. The second creates the local prediction models needed by the Early Support Explorer. The third starts the Streamlit server and opens the dashboard in a browser. Select a subject, enter the six visible student details, and choose Compare prediction stages to see the two estimates. The separate analysis can be rerun with python student_performance.py; it writes the dataset summary, model metrics, and feature-importance tables under results/.')

doc.add_heading('6. Limitations and responsible use', level=1)
for x in [
    'Historical and narrow sample: the data come from two schools in one region and one school year. Performance on other schools, countries, or cohorts is unknown.',
    'Single train/test split: the reported metrics come from one 75/25 split. Repeated stratified cross-validation and uncertainty intervals would provide a more stable assessment.',
    'Not an exact replication: the source paper tested four model families, three input selections, five-level classification, and repeated 10-fold cross-validation. This classroom project uses two tree-based models, two timing scenarios, a binary pass/fail task, and numeric regression.',
    'Association is not causation: feature importance cannot show that absences, family background, or any other variable causes a grade. A predictive model is not a substitute for educational research or professional judgment.',
    'Potential fairness concerns: demographic and social variables can encode unequal conditions. Predictions should support constructive, human-reviewed offers of help, not exclusion, punishment, or fixed labels about student potential.',
    'Prediction uncertainty: an individual estimate can be wrong. The app is a teaching and demonstration tool, not a validated production decision system.'
]: bullet(x)

doc.add_heading('7. Conclusion', level=1)
para('This project provides a practical demonstration of educational data mining. It shows that G1 and G2 are powerful predictors of G3 and that early-warning estimates based on the other recorded characteristics are less precise. The dashboard makes the comparison accessible and offers an illustrative prediction interface. Its appropriate role is to explain model behavior and prompt supportive discussion, while keeping uncertainty, fairness, and the limited scope of the data in view.')

doc.add_heading('References', level=1)
para('Cortez, P. & Silva, A. M. G. (2008). Using data mining to predict secondary school student performance. Proceedings of the 5th Annual Future Business Technology Conference. Paper: https://citeseerx.ist.psu.edu/document?doi=61d468d5254730bbecf822c6b60d7d6595d9889c&repid=rep1&type=pdf')
para('Cortez, P. (2008). Student Performance [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C5TG7T. https://archive.ics.uci.edu/dataset/320/student%2Bperformance')
doc.core_properties.title='Student Performance Prediction Project Report'
doc.core_properties.subject='Detailed explanation of the data mining project and web application'
doc.save(OUT)
print(OUT)
