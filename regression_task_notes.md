# SCMP regression (2018–2024)

## What it does

Weekly OLS for **SCMP only**, testing whether **ad volume** and **HK web traffic** are explained by **content quality** and **political score**.

HKFP and AM730 are excluded for now (HKFP political score gap in late 2024; AM730 quality index not ready).

## Models

1. `Ad = β0 + β1·Quality + β2·PoliticalScore`
2. `Traffic = β0 + β1·Quality + β2·PoliticalScore` — visits, unique visitors, total pages, total time
3. Correlation matrix across all variables

## Variables

| Variable | Source |
|----------|--------|
| Political score | `political_score_weekly.csv` → `south_china_morning_post` |
| Quality index | `quality_index.csv` → weekly mean of `arqi_continuous` |
| Ad volume | `Ad_det_final.csv` → weekly sum of `Ad_Size_Percent` |
| Traffic | `SCMP_hk_marketshare.xlsx` → Weekly Summary, Hong Kong |

## Run

```bash
pip install -r requirements.txt
python run_regression_analysis.py
```

Outputs: `output_regression/weekly_panel.csv`, `ols_results.csv`, `correlations.csv`
