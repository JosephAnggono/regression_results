# Regression task — team notes

## Goal
Test whether **ad volume** and **web traffic** are explained by **content quality** and **political score**, using weekly data for **HKFP, SCMP, and AM730** in one combined panel.

## Variables

| Variable | Source | Weekly value |
|----------|--------|--------------|
| **Political score** | `political_score_weekly.csv` | `political_score` |
| **Quality index** | `quality_index.csv` | mean of `arqi_continuous` per outlet-week |
| **Ad (proxy)** | `Ad_det_final.csv` | sum of `Ad_Size_Percent` per week (`ad_total_size_pct`); backup: `ad_count` |
| **Traffic (HK)** | market share xlsx → Weekly Summary | Visits, Unique Visitors, Total Pages, Total Time Hours |

## Models to run (OLS, pooled)

1. `Ad = β0 + β1·Quality + β2·PoliticalScore`
2. `Traffic_metric = β0 + β1·Quality + β2·PoliticalScore` — repeat for all 4 traffic indicators
3. Correlation matrix: Ad vs each traffic metric (expect Ad–Visits positive)

Run on **combined weekly panel** (all three outlets stacked). Report coefficients, sign, p-value, R², and N.

## Data gaps (important)

| Outlet | Political | Quality | Ads | Traffic |
|--------|-----------|---------|-----|---------|
| HKFP | ✓ | ✓ | ✗ no ad data | ✓ |
| SCMP | ✓ | ✓ | ✓ | ✓ |
| AM730 | ✓ | ✗ no quality data | ✓ | ✓ |

- **Ad ~ Quality + Political**: only **SCMP** has all three variables.
- **Traffic ~ Quality + Political**: **HKFP + SCMP** only (AM730 excluded).
- **Ad ~ Traffic correlation**: **SCMP + AM730** only (HKFP excluded).

Note these limits when interpreting results.

## Outlet name mapping

| Outlet | Political `source_file` | Quality `outlet` | Ads `Newspaper` |
|--------|-------------------------|------------------|-----------------|
| HKFP | `hkfp` | `hong_kong_free_press` | — |
| SCMP | `south_china_morning_post` | `south_china_morning_post` | `SCMP` |
| AM730 | `am730` | — | `am730` |

## How to run

**Yes — someone needs to run this locally** after pulling the repo. GitHub only stores the code and results; it does not run the script automatically.

```bash
pip install pandas openpyxl statsmodels
python run_regression_analysis.py
```

Outputs are written to `output_regression/`:
- `weekly_panel.csv` — merged dataset
- `ols_results.csv` — all coefficients
- `correlations.csv` — correlation table

## GitHub

Repo: **https://github.com/JosephAnggono/regression_results**

After updating data or code, re-run the script, then commit and push the new CSVs so the team sees the latest results.

## What to report back

For each model: coefficient on Quality, coefficient on Political Score, whether each is positive/negative, p-value, and whether it supports or rejects the hypothesis.

Expected hypotheses (to verify, not assume):
- Quality ↑ → Ads ↑
- Quality ↑ → Traffic ↑
- Ad ↔ Visits: positive correlation
- Political score effect: sign depends on outlet mix / period — report what the data shows
