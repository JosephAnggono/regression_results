"""SCMP weekly OLS: ads and traffic vs quality index and political score (2018–2024)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"
OUT = REPO / "output_regression"

OUTLET = "SCMP"
YEAR_MIN, YEAR_MAX = 2018, 2024

POLITICAL_CSV = DATA / "political_score_weekly.csv"
QUALITY_CSV = DATA / "quality_index.csv"
AD_CSV = DATA / "Ad_det_final.csv"
TRAFFIC_XLSX = DATA / "SCMP_hk_marketshare.xlsx"

POLITICAL_KEY = "south_china_morning_post"
QUALITY_KEY = "south_china_morning_post"
AD_KEY = "SCMP"

TRAFFIC_COLS = {
    "visits": "Visits",
    "unique_visitors": "Unique Visitors",
    "total_pages": "Estimated Total Pages",
    "total_time_hours": "Estimated Total Time Hours",
}


def iso_week(dt: pd.Series) -> pd.Series:
    return pd.to_datetime(dt).dt.strftime("%G-W%V")


def week_year(week: pd.Series) -> pd.Series:
    return week.str.slice(0, 4).astype(int)


def load_political() -> pd.DataFrame:
    df = pd.read_csv(POLITICAL_CSV)
    df = df[df["source_file"] == POLITICAL_KEY][["week", "political_score"]]
    return df[(week_year(df["week"]) >= YEAR_MIN) & (week_year(df["week"]) <= YEAR_MAX)]


def load_quality() -> pd.DataFrame:
    df = pd.read_csv(QUALITY_CSV, usecols=["outlet", "publish_date", "arqi_continuous"])
    df = df[df["outlet"] == QUALITY_KEY].copy()
    df["week"] = iso_week(df["publish_date"])
    df = df[(week_year(df["week"]) >= YEAR_MIN) & (week_year(df["week"]) <= YEAR_MAX)]
    return (
        df.groupby("week", as_index=False)["arqi_continuous"]
        .mean()
        .rename(columns={"arqi_continuous": "quality_index"})
    )


def load_ads() -> pd.DataFrame:
    df = pd.read_csv(AD_CSV, encoding="utf-8-sig")
    df = df[df["Newspaper"] == AD_KEY].copy()
    df["week"] = iso_week(df["Date"])
    df = df[(week_year(df["week"]) >= YEAR_MIN) & (week_year(df["week"]) <= YEAR_MAX)]
    return df.groupby("week", as_index=False).agg(ad_total_size_pct=("Ad_Size_Percent", "sum"))


def load_traffic() -> pd.DataFrame:
    ws = pd.read_excel(TRAFFIC_XLSX, sheet_name="Weekly Summary", header=2)
    hk = ws[ws["Region"] == "Hong Kong"].copy()
    hk["week"] = iso_week(hk["Week Start"])
    hk = hk[(week_year(hk["week"]) >= YEAR_MIN) & (week_year(hk["week"]) <= YEAR_MAX)]
    keep = ["week"] + list(TRAFFIC_COLS.values())
    return hk[keep].rename(columns={v: k for k, v in TRAFFIC_COLS.items()})


def build_panel() -> pd.DataFrame:
    panel = load_traffic()
    for loader in (load_political, load_quality, load_ads):
        panel = panel.merge(loader(), on="week", how="inner")
    return panel.sort_values("week").reset_index(drop=True)


def run_ols(y: pd.Series, X: pd.DataFrame, model_name: str) -> list[dict]:
    data = pd.concat([y, X], axis=1).dropna()
    X_clean = sm.add_constant(data.iloc[:, 1:])
    fit = sm.OLS(data.iloc[:, 0], X_clean).fit()
    return [
        {
            "model": model_name,
            "n": int(fit.nobs),
            "term": name,
            "coef": fit.params[name],
            "pvalue": fit.pvalues[name],
            "r_squared": fit.rsquared,
        }
        for name in X_clean.columns
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = build_panel()
    panel.to_csv(OUT / "weekly_panel.csv", index=False)

    predictors = panel[["quality_index", "political_score"]]
    results: list[dict] = []
    results.extend(run_ols(panel["ad_total_size_pct"], predictors, "ad_total_size_pct"))
    for metric in TRAFFIC_COLS:
        results.extend(run_ols(panel[metric], predictors, metric))

    pd.DataFrame(results).to_csv(OUT / "ols_results.csv", index=False)

    cols = ["ad_total_size_pct", "quality_index", "political_score"] + list(TRAFFIC_COLS.keys())
    panel[cols].corr(numeric_only=True).to_csv(OUT / "correlations.csv")

    print(f"SCMP panel rows ({YEAR_MIN}-{YEAR_MAX}): {len(panel)}")
    print(f"Weeks: {panel['week'].min()} to {panel['week'].max()}")
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    main()
