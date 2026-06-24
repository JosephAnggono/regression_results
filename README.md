# SCMP regression results

Weekly OLS for **SCMP** (2018–2024): ads and HK traffic vs content quality and political score.

HKFP and AM730 excluded — HKFP political score incomplete in late 2024; AM730 quality index not ready.

**Sample:** 300 weeks (2018-W31 to 2024-W52), all variables present.

## OLS coefficients

| Outcome | Quality (β₁) | p | Political (β₂) | p | R² |
|---------|-------------|---|----------------|---|-----|
| **Ad volume** | +21.5 | 0.54 | −0.07 | 0.85 | 0.001 |
| **Visits** | −607,163 | **0.001** | +1,586 | 0.43 | 0.035 |
| **Unique visitors** | −371,534 | **0.004** | +415 | 0.76 | 0.027 |
| **Total pages** | −1,845,525 | **0.002** | −2,685 | 0.67 | 0.033 |
| **Total time** | −295,628 | **0.0004** | +5 | 1.00 | 0.041 |

**Ad model:** Neither quality nor political score is significant.

**Traffic models:** Quality is significantly **negative** on all four metrics. Political score is not significant.

## Key correlations

| Pair | r |
|------|---|
| Ad ↔ Visits | −0.08 |
| Ad ↔ Quality | +0.04 |
| Quality ↔ Visits | −0.18 |
| Political ↔ Visits | +0.04 |

## Files

- `output_regression/weekly_panel.csv` — merged weekly data
- `output_regression/ols_results.csv` — full coefficients
- `output_regression/correlations.csv` — correlation matrix

## Run locally

```bash
pip install -r requirements.txt
python run_regression_analysis.py
```

Input files go in `data/` (see `data/README.md`).
