# SCMP regression (2018–2024)

## What it does

Weekly analysis for **SCMP only**: test whether **HK web traffic** is explained by **content quality** and **political score**.

## Models

`Traffic = β0 + β1·Quality + β2·PoliticalScore` — OLS for visits, unique visitors, total pages, total time.

## Correlation

**Pearson correlation (r)** between all variables on the same weekly panel.

Used because every variable is continuous numeric weekly data and we want the strength of a **linear** relationship between two variables.

## Variables

| Variable | Source |
|----------|--------|
| Political score | `political_score_weekly.csv` |
| Quality index | `quality_index.csv` — weekly mean of `arqi_continuous` |
| Traffic | `SCMP_hk_marketshare.xlsx` — Weekly Summary, Hong Kong |

## Run

```bash
pip install -r requirements.txt
python run_regression_analysis.py
```
