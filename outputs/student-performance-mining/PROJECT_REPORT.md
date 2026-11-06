# Project report: using data mining to predict student performance

## Aim

Reproduce the central question in Cortez and Silva (2008): can demographic, social, school and previous-grade data help estimate final secondary-school performance in Mathematics and Portuguese? The paper tested regression, pass/fail and five-level classification, and compared setups with different grade information. Its main conclusion was that first- and second-period grades improve prediction substantially, while absences, previous failures and other school/social variables can still be informative.

## Dataset profile

The supplied files each have 33 columns and no missing cells or duplicate rows. Mathematics contains 395 students; Portuguese contains 649. Mean final grade (`G3`) is 10.415/20 for Mathematics and 11.906/20 for Portuguese. The proportion scoring at least 10 is 67.1% and 84.6%, respectively. These datasets represent two schools in Portugal in 2005–2006 and should not be assumed representative of other populations.

## Experiment and results

The included Python program uses a fixed 75/25 random train/test split (seed 42), one-hot encodes categories, and compares decision trees and random forests. Regression estimates numeric `G3`; classification predicts pass (`G3 >= 10`) or fail. The two scenarios exclude or include G1 and G2. The recorded random-forest results are:

| Subject | Inputs | MAE | RMSE | R² | Pass/fail accuracy | Pass/fail macro-F1 |
|---|---|---:|---:|---:|---:|---:|
| Mathematics | Early warning, no G1/G2 | 3.057 | 3.791 | 0.376 | 0.687 | 0.633 |
| Mathematics | In-year, with G1/G2 | 1.094 | 1.789 | 0.861 | 0.909 | 0.904 |
| Portuguese | Early warning, no G1/G2 | 2.081 | 2.840 | 0.200 | 0.834 | 0.664 |
| Portuguese | In-year, with G1/G2 | 0.734 | 1.165 | 0.865 | 0.896 | 0.789 |

Including G1/G2 substantially improves grade regression in both subjects. Pass/fail accuracy rises for Mathematics; for Portuguese, the early-warning accuracy is already high because most students pass, and the modest accuracy gain should be read alongside macro-F1, which weights both classes equally. The single holdout split makes these estimates illustrative; repeated cross-validation would give a more stable comparison.

In the early-warning random forest, the largest feature-importance rankings are `absences` (0.194) and `failures` (0.138) for Mathematics; `failures` (0.252) and `absences` (0.061) for Portuguese. Importance values describe this fitted model's predictive splits, not causes or intervention effects. Rankings can change with the sample and model.

## Conclusion

The results support the paper's central finding that previous grades are highly informative for predicting the final grade. Early prediction without those grades is much less precise, although the models still capture some signal from attendance, prior failures and other recorded attributes. A school could use this kind of analysis to inform supportive conversations, but the model should not determine student opportunities or label students as destined to fail. These are historical observational records, and no causal conclusions follow from the model.

## Reproducibility and limits

Run `python student_performance.py` from this directory after installing `requirements.txt`. The script writes the exact metrics and feature rankings to `results/`. This compact project does not replicate all four model types, all three prediction tasks or the paper's repeated 10-fold validation. It does not implement the five-level grade task. The supplied R script joins two subject files using a subset of attributes rather than a unique student identifier; this can create ambiguous many-to-many matches, so no cross-subject merged sample is used here.

## References

Cortez, P. & Silva, A. M. G. (2008). *Using data mining to predict secondary school student performance*. Proceedings of the 5th Annual Future Business Technology Conference. [Paper PDF](https://citeseerx.ist.psu.edu/document?doi=61d468d5254730bbecf822c6b60d7d6595d9889c&repid=rep1&type=pdf).

Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning Repository. [Dataset record](https://archive.ics.uci.edu/dataset/320/student%2Bperformance). DOI: 10.24432/C5TG7T.
