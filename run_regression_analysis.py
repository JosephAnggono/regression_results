"""SCMP weekly regression: OLS vs HC3 robust SE (2018–2024)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm

from regression_lib import ANALYSIS_COLS, TRAFFIC_COLS, YEAR_MAX, YEAR_MIN, build_panel

REPO = Path(__file__).resolve().parent
OUT = REPO / "output_regression"


def run_regression(
    y: pd.Series,
    X: pd.DataFrame,
    outcome: str,
    estimator: str,
) -> list[dict]:
    data = pd.concat([y, X], axis=1).dropna()
    X_clean = sm.add_constant(data.iloc[:, 1:])
    y_clean = data.iloc[:, 0]
    if estimator == "hc3":
        fit = sm.OLS(y_clean, X_clean).fit(cov_type="HC3")
    else:
        fit = sm.OLS(y_clean, X_clean).fit()

    rows = []
    for name in X_clean.columns:
        rows.append(
            {
                "outcome": outcome,
                "estimator": estimator,
                "n": int(fit.nobs),
                "term": name,
                "coef": fit.params[name],
                "std_err": fit.bse[name],
                "pvalue": fit.pvalues[name],
                "r_squared": fit.rsquared,
            }
        )
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = build_panel()
    panel.to_csv(OUT / "weekly_panel.csv", index=False)

    predictors = panel[["quality_index", "political_score"]]
    results: list[dict] = []
    for metric in TRAFFIC_COLS:
        results.extend(run_regression(panel[metric], predictors, metric, "ols"))
        results.extend(run_regression(panel[metric], predictors, metric, "hc3"))

    pd.DataFrame(results).to_csv(OUT / "ols_results.csv", index=False)
    panel[ANALYSIS_COLS].corr(method="pearson").to_csv(OUT / "correlations_pearson.csv")
    panel[ANALYSIS_COLS].corr(method="spearman").to_csv(OUT / "correlations_spearman.csv")

    print(f"SCMP panel rows ({YEAR_MIN}-{YEAR_MAX}): {len(panel)}")
    print(f"Weeks: {panel['week'].min()} to {panel['week'].max()}")
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    main()
