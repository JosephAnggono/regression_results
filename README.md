# SCMP regression results

Weekly OLS for **SCMP** (2018–2024): HK traffic vs content quality and political score.

**Sample:** 365 weeks (2018-W01 to 2024-W52). Ads removed from this analysis.

## OLS coefficients

| Outcome | Quality (β₁) | p | Political (β₂) | p | R² |
|---------|-------------|---|----------------|---|-----|
| **Visits** | −741,648 | **0.00003** | +1,732 | 0.37 | 0.048 |
| **Unique visitors** | −438,714 | **0.0002** | +522 | 0.69 | 0.037 |
| **Total pages** | −2,070,121 | **0.0001** | −3,078 | 0.60 | 0.040 |
| **Total time** | −327,590 | **0.00002** | −0.09 | 1.00 | 0.050 |

**Quality:** Significantly **negative** on all four traffic metrics — higher quality weeks align with lower traffic, holding political score constant.

**Political score:** Not significant on any traffic metric.

## Correlations (Pearson r)

| Pair | r | Interpretation |
|------|---|----------------|
| Quality ↔ Visits | **−0.22** | Weak negative linear association |
| Quality ↔ Unique visitors | −0.19 | Weak negative |
| Quality ↔ Total pages | −0.20 | Weak negative |
| Quality ↔ Total time | −0.23 | Weak negative |
| Political ↔ Visits | +0.04 | No meaningful linear association |
| Visits ↔ Unique visitors | +0.97 | Very strong (metrics move together) |

**Correlation type:** Pearson product-moment correlation (r).

**Why Pearson:** All variables are continuous weekly numbers. Pearson measures how closely two variables move together in a **straight-line** pattern. It is the standard choice here and matches the OLS setup (linear regression). It does not detect non-linear patterns and can be pulled by extreme weeks.

## Files

- `output_regression/weekly_panel.csv`
- `output_regression/ols_results.csv`
- `output_regression/correlations.csv`

## Run

```bash
pip install -r requirements.txt
python run_regression_analysis.py
```

Input files: `data/README.md`
