# Collaborative Robot Selection for CNC Machine Tending

## Project Summary

This project explores how a transparent multi-criteria decision-making model could support the selection of a collaborative robot system for CNC machine tending in a small or medium-sized manufacturing facility.

The work is being developed in two phases:

1. **Paper reproduction and audit:** understand, reproduce, and critically examine a published entropy-AHP-TOPSIS supplier-selection model.
2. **Robotics extension:** transfer the method to a separate cobot-selection dataset with explicit eligibility rules, data provenance, stakeholder priorities, and sensitivity analysis.

The paper's building-material supplier data will not be presented as robotics data. The robotics extension will use its own dataset and will label each value as public/verified, estimated, proxied, or synthetic.

## Current Status

**Phase 1 is in progress.** The raw decision matrix and main calculations have been reproduced. The audit identified areas where the published results cannot be regenerated directly from the displayed inputs and equations.

The robotics ranking and product MVP have not yet been completed.

## Project Files

- [Executed reproduction and audit notebook](notebooks/01_paper_reproduction_and_audit.ipynb)
- [Formula-driven learning workbook](docs/TOPSIS_Paper_Reproduction_Learning_Workbook.xlsx)
- [Paper decision matrix](data/paper_decision_matrix.csv)
- [Paper data dictionary](data/paper_data_dictionary.csv)

## Research Question

How can subjective stakeholder priorities and objective differences in supplier data be combined to support a transparent supplier-selection decision?

## Source Paper

Chen, C.-H. (2020). “A Novel Multi-Criteria Decision-Making Model for Building Material Supplier Selection Based on Entropy-AHP Weighted TOPSIS.” *Entropy*, 22(2), 259. [https://doi.org/10.3390/e22020259](https://doi.org/10.3390/e22020259)

## Method at a Glance

| Stage | Question answered |
|---|---|
| Criteria design | What factors are relevant, and which are benefits, costs, or mandatory requirements? |
| AHP | What do decision-makers consider important? |
| Entropy weighting | Which criteria distinguish the suppliers in the observed data? |
| Combined weighting | How can stakeholder priorities and data-based variation be reconciled? |
| TOPSIS | Which eligible alternative is closest to the ideal solution and farthest from the worst solution? |
| Sensitivity analysis | Does the recommendation remain stable when reasonable assumptions change? |

## One Entropy Example: C1

C1 is the qualified-products rate. After benefit-direction min-max rescaling, the five supplier values become approximately:

```text
A1 = 0.5714
A2 = 1.0000
A3 = 0.2857
A4 = 0.0000
A5 = 0.1429
```

Their sum is `2.0000`. Dividing each value by that total produces proportions of approximately `0.2857`, `0.5000`, `0.1429`, `0.0000`, and `0.0714`. These proportions sum to one and form the distribution used by the entropy formula.

For C1:

```text
Entropy                  = 0.7276
Information utility 1-e  = 0.2724
Local objective weight   = 0.3861 (within its three-criterion group)
```

The local objective weight is not C1's influence over the complete model. A global criterion weight must also account for the weight of C1's group.

## Reproduction Findings

### Results reported by the paper

| Supplier | Published closeness | Published rank |
|---|---:|---:|
| A1 | 0.6395 | 1 |
| A2 | 0.2326 | 5 |
| A3 | 0.5946 | 2 |
| A4 | 0.5350 | 3 |
| A5 | 0.3074 | 4 |

Published ranking: **A1 > A3 > A4 > A5 > A2**.

### Equation-consistent calculation

Applying every published final criterion weight consistently to the paper's column-sum-normalized decision matrix gives:

| Supplier | Recalculated closeness | Recalculated rank |
|---|---:|---:|
| A1 | 0.5220 | 3 |
| A2 | 0.3010 | 5 |
| A3 | 0.6695 | 1 |
| A4 | 0.5852 | 2 |
| A5 | 0.3876 | 4 |

Equation-consistent ranking: **A3 > A4 > A1 > A5 > A2**.

## Audit Findings

1. **The original AHP judgments are unavailable.** The paper reports AHP weights but does not provide the complete expert pairwise-comparison matrices or consistency ratios needed to regenerate those weights from the original judgments. The notebook therefore treats the published AHP weights as source inputs.

2. **The C4-C5 entropy weights do not reproduce from the displayed data and equations.** Direct recalculation gives approximately `0.6199` and `0.3801`; the paper reports `0.4658` and `0.5342`. The C1-C3 and C6-C7 local entropy weights reproduce closely.

3. **The published TOPSIS ranking does not follow from consistent application of the published final weights.** The published closeness values can be recreated to displayed precision by reproducing an apparent weighted-matrix reference pattern: C3 uses the C2 weight for all suppliers, while A1's C2 cell uses the C3 weight. This is documented as an apparent inconsistency, not as evidence of intent.

4. **The paper uses column-sum normalization in its TOPSIS calculation.** This reproduction follows that choice. Vector normalization is a common alternative and will be considered later as a robustness test, not silently substituted into the reproduction.

## Interpretation

The exercise is a reproduction **and audit**, not a claim that every published result was independently validated. It demonstrates why transparent formulas, source labeling, and sensitivity testing are essential when a model may influence a sourcing decision.

## Repository Structure

```text
01-robotics-supplier-selection/
├── README.md
├── data/
│   ├── paper_decision_matrix.csv
│   └── paper_data_dictionary.csv
├── notebooks/
│   └── 01_paper_reproduction_and_audit.ipynb
├── docs/
│   └── TOPSIS_Paper_Reproduction_Learning_Workbook.xlsx
└── outputs/
```

The notebook is the primary reproducible analysis. The data dictionary documents each criterion's direction, reported unit, source role, and reproduction status. The workbook provides the same learning path with visible spreadsheet formulas and separate validation sheets.

## Run the Notebook

From this project folder:

```bash
python -m pip install -r requirements.txt
jupyter notebook notebooks/01_paper_reproduction_and_audit.ipynb
```

The notebook reads the included CSV and calculates the entropy and TOPSIS results from the source values.

## Planned Robotics Extension

The next phase will define:

- the CNC machine-tending workflow and primary users;
- mandatory requirements that must be passed before ranking;
- relevant benefit and cost criteria;
- a data dictionary and source-quality labels;
- stakeholder-priority collection using AHP;
- a separate cobot dataset;
- scenario and sensitivity analysis; and
- a small interactive decision-support prototype.

The extension will not describe the MCDM model itself as machine learning. Any later AI capability must solve a defined user problem and receive its own evaluation and limitations analysis.

## Limitations

- Anonymous alternatives prevent independent verification of the original supplier data.
- Missing AHP judgment matrices limit full reproducibility.
- Entropy measures data variation, not business importance.
- TOPSIS permits compensation unless mandatory requirements are screened beforehand.
- A ranking depends on criteria, weights, normalization, data quality, and modeling choices.
