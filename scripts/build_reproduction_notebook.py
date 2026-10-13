from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "projects/01-robotics-supplier-selection/notebooks/01_paper_reproduction_and_audit.ipynb"
CELL_IDS = iter(range(100))


def markdown(text):
    return {
        "cell_type": "markdown",
        "id": f"cell-{next(CELL_IDS):03d}",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


def code(text):
    return {
        "cell_type": "code",
        "id": f"cell-{next(CELL_IDS):03d}",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

nb["cells"] = [
    markdown(
        """
# Entropy-AHP-TOPSIS Paper Reproduction and Audit

This notebook reproduces the supplier-selection calculations reported in Chen (2020) and separates:

1. values directly reported by the paper;
2. results obtained by applying the displayed equations consistently; and
3. an apparent weighted-matrix reference pattern that recreates the published TOPSIS output.

The purpose is learning and methodological audit. The paper's building-material supplier data is not robotics data and will not be mixed into the later collaborative-robot extension.

**Source:** Chun-Ho Chen (2020), "A Novel Multi-Criteria Decision-Making Model for Building Material Supplier Selection Based on Entropy-AHP Weighted TOPSIS," *Entropy*, 22(2), 259. https://doi.org/10.3390/e22020259
"""
    ),
    code(
        """
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display

pd.options.display.float_format = "{:.4f}".format

project_dir = Path.cwd()
if project_dir.name == "notebooks":
    project_dir = project_dir.parent
elif not (project_dir / "data/paper_decision_matrix.csv").exists():
    candidate = project_dir / "projects/01-robotics-supplier-selection"
    if candidate.exists():
        project_dir = candidate

data_path = project_dir / "data/paper_decision_matrix.csv"
raw = pd.read_csv(data_path).set_index("supplier")
raw
"""
    ),
    markdown(
        """
## 1. Decision Matrix and Criterion Direction

The paper evaluates five anonymous suppliers (A1-A5) using seven criteria. Benefit criteria favor higher values; cost criteria favor lower values.
"""
    ),
    code(
        """
criteria = pd.DataFrame(
    {
        "code": ["C1", "C2", "C3", "C4", "C5", "C6", "C7"],
        "criterion": [
            "Qualified-products rate",
            "Product price",
            "Market share",
            "Supply capacity",
            "New-product development rate",
            "Delivery time",
            "On-time delivery ratio",
        ],
        "group": [
            "Product Satisfaction",
            "Product Satisfaction",
            "Product Satisfaction",
            "Supply Innovation",
            "Supply Innovation",
            "Service Level",
            "Service Level",
        ],
        "direction": ["benefit", "cost", "benefit", "benefit", "benefit", "cost", "benefit"],
    }
).set_index("code")

raw.columns = criteria.index
display(criteria)
display(raw)
"""
    ),
    markdown(
        """
## 2. Entropy Weighting

Entropy weighting asks how strongly each criterion distinguishes the observed suppliers. The calculation used here follows three steps:

1. Rescale benefit and cost criteria to a common 0-1 direction.
2. Convert each criterion column into proportions that sum to one.
3. Calculate entropy, information utility (`1 - entropy`), and local objective weights within each criterion group.

High entropy means the supplier proportions are relatively even and the criterion provides less distinguishing information. Low entropy means the distribution is more concentrated and the criterion provides more distinguishing information. Variation is not the same as business importance; that is why the method also uses AHP.
"""
    ),
    code(
        """
benefit = criteria["direction"].eq("benefit").to_numpy()
x = raw.to_numpy(dtype=float)
x_min = x.min(axis=0)
x_max = x.max(axis=0)

rescaled = np.where(
    benefit,
    (x - x_min) / (x_max - x_min),
    (x_max - x) / (x_max - x_min),
)
rescaled = pd.DataFrame(rescaled, index=raw.index, columns=raw.columns)

proportions = rescaled / rescaled.sum(axis=0)
p = proportions.to_numpy()
p_log_p = np.zeros_like(p)
positive = p > 0
p_log_p[positive] = p[positive] * np.log(p[positive])

entropy = -p_log_p.sum(axis=0) / np.log(len(raw))
utility = 1 - entropy

entropy_summary = pd.DataFrame(
    {"entropy": entropy, "information_utility": utility},
    index=raw.columns,
)

entropy_summary["recalculated_local_weight"] = np.nan
for group in criteria["group"].unique():
    members = criteria.index[criteria["group"].eq(group)]
    entropy_summary.loc[members, "recalculated_local_weight"] = (
        entropy_summary.loc[members, "information_utility"]
        / entropy_summary.loc[members, "information_utility"].sum()
    )

published_entropy_local = pd.Series(
    [0.3862, 0.2641, 0.3497, 0.4658, 0.5342, 0.4168, 0.5832],
    index=raw.columns,
    name="published_local_weight",
)
entropy_summary = entropy_summary.join(published_entropy_local)
entropy_summary["difference"] = (
    entropy_summary["recalculated_local_weight"]
    - entropy_summary["published_local_weight"]
)

print("Direction-aware rescaling")
display(rescaled)
print("Proportions used by entropy")
display(proportions)
print("Entropy audit")
display(entropy_summary)
"""
    ),
    markdown(
        """
### Worked C1 Interpretation

For C1, the rescaled values sum to 2. A2's rescaled value is 1, so its proportion is `1 / 2 = 0.5`. This does not mean A2 has 50% quality or that C1 has a 50% weight. It means A2 contributes half of the total rescaled C1 distribution.

The C1 entropy is approximately `0.7276`; its information utility is approximately `0.2724`. Dividing that utility by the combined utility of C1-C3 produces a local objective weight of approximately `0.3861` within the Product Satisfaction group.

The audit table shows that C1-C3 and C6-C7 reproduce closely. C4-C5 do not: the equations and displayed data give approximately `0.6199` and `0.3801`, while the paper reports `0.4658` and `0.5342`.
"""
    ),
    markdown(
        """
## 3. Published AHP and Final Weights

AHP represents stakeholder priorities. The paper reports AHP weights, but it does not provide the complete original pairwise-comparison matrices or consistency ratios required to regenerate those judgments. This notebook therefore treats the reported AHP and final combined weights as sourced inputs rather than independently reproduced outputs.
"""
    ),
    code(
        """
published_ahp = pd.DataFrame(
    {
        "group": criteria["group"],
        "local_ahp_weight": [0.4125, 0.3759, 0.2116, 0.5293, 0.4707, 0.3917, 0.6083],
    },
    index=raw.columns,
)

published_final_weights = pd.Series(
    [0.2415, 0.1505, 0.1122, 0.1051, 0.1071, 0.0894, 0.1942],
    index=raw.columns,
    name="published_final_weight",
)

display(published_ahp.join(published_final_weights))
print(f"Final weights sum to {published_final_weights.sum():.4f}")
"""
    ),
    markdown(
        """
## 4. Equation-Consistent TOPSIS

The paper uses column-sum normalization in its TOPSIS calculation. This reproduction follows that reported choice rather than silently replacing it with vector normalization.

The ideal best uses the maximum weighted value for benefit criteria and minimum weighted value for cost criteria. The ideal worst reverses those directions. Each supplier's closeness score is its distance from the ideal worst divided by the sum of its distances from both ideals.
"""
    ),
    code(
        """
def topsis(weighted_matrix, benefit_mask):
    values = np.asarray(weighted_matrix, dtype=float)
    ideal_best = np.where(benefit_mask, values.max(axis=0), values.min(axis=0))
    ideal_worst = np.where(benefit_mask, values.min(axis=0), values.max(axis=0))
    distance_best = np.sqrt(((values - ideal_best) ** 2).sum(axis=1))
    distance_worst = np.sqrt(((values - ideal_worst) ** 2).sum(axis=1))
    closeness = distance_worst / (distance_best + distance_worst)
    return closeness, ideal_best, ideal_worst


column_sum_normalized = raw / raw.sum(axis=0)
weighted_consistent = column_sum_normalized * published_final_weights
consistent_closeness, ideal_best, ideal_worst = topsis(weighted_consistent, benefit)

consistent_results = pd.DataFrame(
    {"equation_consistent_closeness": consistent_closeness},
    index=raw.index,
)
consistent_results["equation_consistent_rank"] = (
    consistent_results["equation_consistent_closeness"]
    .rank(ascending=False, method="min")
    .astype(int)
)

display(weighted_consistent)
display(consistent_results.sort_values("equation_consistent_rank"))
"""
    ),
    markdown(
        """
## 5. Published-Output Reconstruction

Applying every published final weight consistently produces `A3 > A4 > A1 > A5 > A2`, not the published ranking.

The published closeness values can be recreated to displayed precision by reproducing an apparent weighted-matrix reference pattern visible in the paper's tables:

- C3 uses the C2 weight for all five suppliers.
- A1's C2 cell uses the C3 weight.
- All other cells use their stated criterion weights.

This is documented as an apparent reference inconsistency based on the displayed data and equations. It is not presented as evidence of intent.
"""
    ),
    code(
        """
weight_matrix = np.tile(published_final_weights.to_numpy(), (len(raw), 1))
weight_matrix[:, 2] = published_final_weights["C2"]
weight_matrix[0, 1] = published_final_weights["C3"]

weighted_published_path = column_sum_normalized.to_numpy() * weight_matrix
published_path_closeness, _, _ = topsis(weighted_published_path, benefit)

reported_closeness = pd.Series(
    [0.6395, 0.2326, 0.5946, 0.5350, 0.3074],
    index=raw.index,
    name="paper_reported_closeness",
)

comparison = pd.DataFrame(
    {
        "paper_reported": reported_closeness,
        "published_path_recreated": published_path_closeness,
        "equation_consistent": consistent_closeness,
    },
    index=raw.index,
)
comparison["recreated_minus_reported"] = (
    comparison["published_path_recreated"] - comparison["paper_reported"]
)
display(comparison)

ax = comparison[["paper_reported", "equation_consistent"]].plot(
    kind="bar", figsize=(9, 4.5), color=["#178582", "#D97706"]
)
ax.set_title("Published vs. Equation-Consistent TOPSIS Closeness")
ax.set_xlabel("Supplier")
ax.set_ylabel("Closeness score")
ax.set_ylim(0, 0.75)
ax.legend(["Paper reported", "Equation-consistent"], frameon=False)
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
"""
    ),
    code(
        """
expected_consistent = np.array([0.5220, 0.3010, 0.6695, 0.5852, 0.3876])
expected_published_path = reported_closeness.to_numpy()

assert np.allclose(consistent_closeness, expected_consistent, atol=0.0001)
assert np.allclose(published_path_closeness, expected_published_path, atol=0.0002)
assert np.isclose(published_final_weights.sum(), 1.0)
assert np.allclose(proportions.sum(axis=0), 1.0)

print("Validation checks passed.")
"""
    ),
    markdown(
        """
## 6. What Was and Was Not Reproduced

**Reproduced closely**

- The raw supplier decision matrix.
- C1-C3 and C6-C7 local entropy weights.
- The paper's published TOPSIS scores when the apparent weighted-matrix reference pattern is explicitly recreated.

**Not independently reproducible from the published information**

- The original AHP weights from raw expert judgments, because complete pairwise matrices and consistency results are not reported.
- The published C4-C5 local entropy weights from the displayed raw data and equations.
- The published TOPSIS ranking when every published final criterion weight is applied consistently.

## 7. Implications for the Robotics Extension

The robotics extension will be developed as a separate decision problem. It will:

- define mandatory eligibility requirements before ranking;
- use a separate cobot dataset with source-quality labels;
- distinguish stakeholder judgments from observed specifications;
- keep synthetic assumptions explicit;
- test ranking stability under alternative weights and scenarios; and
- treat the output as decision support rather than an automatic purchasing decision.

The extension will not call entropy-AHP-TOPSIS a machine-learning model. A future AI capability will be added only if it addresses a validated user need and can be evaluated separately.
"""
    ),
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print(f"Wrote {OUTPUT}")
