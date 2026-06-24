"""
OLS regression: Ad and traffic vs quality index and political score.
Outlets: HKFP, SCMP, AM730 (combined weekly panel).

Place input files in ./data/ (see data/README.md).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"
OUT = REPO / "output_regression"

POLITICAL_CSV = DATA / "political_score_weekly.csv"
QUALITY_CSV = DATA / "quality_index.csv"
AD_CSV = DATA / "Ad_det_final.csv"

TRAFFIC_FILES = {
    "HKFP": DATA / "HKFP_hk_marketshare.xlsx",
    "SCMP": DATA / "SCMP_hk_marketshare.xlsx",
    "AM730": DATA / "AM730_hk_marketshare.xlsx",
}

POLITICAL_MAP = {"am730": "AM730", "hkfp": "HKFP", "south_china_morning_post": "SCMP"}
QUALITY_MAP = {"hong_kong_free_press": "HKFP", "south_china_morning_post": "SCMP"}
AD_MAP = {"SCMP": "SCMP", "am730": "AM730"}

TRAFFIC_COLS = {
    "visits": "Visits",
    "unique_visitors": "Unique Visitors",
    "total_pages": "Estimated Total Pages",
    "total_time_hours": "Estimated Total Time Hours",
}


def iso_week(dt: pd.Series) -> pd.Series:
    return pd.to_datetime(dt).dt.strftime("%G-W%V")


def load_political() -> pd.DataFrame:
    df = pd.read_csv(POLITICAL_CSV)
    df = df[df["source_file"].isin(POLITICAL_MAP)].copy()
    df["outlet"] = df["source_file"].map(POLITICAL_MAP)
    return df[["outlet", "week", "political_score"]]


def load_quality() -> pd.DataFrame:
    df = pd.read_csv(QUALITY_CSV, usecols=["outlet", "publish_date", "arqi_continuous"])
    df = df[df["outlet"].isin(QUALITY_MAP)].copy()
    df["outlet"] = df["outlet"].map(QUALITY_MAP)
    df["week"] = iso_week(df["publish_date"])
    return df.groupby(["outlet", "week"], as_index=False)["arqi_continuous"].mean().rename(
        columns={"arqi_continuous": "quality_index"}
    )


def load_ads() -> pd.DataFrame:
    df = pd.read_csv(AD_CSV, encoding="utf-8-sig")
    df = df[df["Newspaper"].isin(AD_MAP)].copy()
    df["outlet"] = df["Newspaper"].map(AD_MAP)
    df["week"] = iso_week(df["Date"])
    return df.groupby(["outlet", "week"], as_index=False).agg(
        ad_count=("Ad_Size_Percent", "size"),
        ad_total_size_pct=("Ad_Size_Percent", "sum"),
    )


def load_traffic() -> pd.DataFrame:
    frames = []
    for outlet, path in TRAFFIC_FILES.items():
        ws = pd.read_excel(path, sheet_name="Weekly Summary", header=2)
        hk = ws[ws["Region"] == "Hong Kong"].copy()
        hk["outlet"] = outlet
        hk["week"] = iso_week(hk["Week Start"])
        keep = ["outlet", "week"] + list(TRAFFIC_COLS.values())
        frames.append(hk[keep])
    merged = pd.concat(frames, ignore_index=True)
    return merged.rename(columns={v: k for k, v in TRAFFIC_COLS.items()})


def build_panel() -> pd.DataFrame:
    panel = load_traffic()
    panel = panel.merge(load_political(), on=["outlet", "week"], how="left")
    panel = panel.merge(load_quality(), on=["outlet", "week"], how="left")
    panel = panel.merge(load_ads(), on=["outlet", "week"], how="left")
    return panel.sort_values(["outlet", "week"]).reset_index(drop=True)


def run_ols(y: pd.Series, X: pd.DataFrame, model_name: str) -> list[dict]:
    data = pd.concat([y, X], axis=1).dropna()
    if len(data) < 10:
        return [{"model": model_name, "n": len(data), "term": "error", "coef": None, "pvalue": None, "r_squared": None}]
    y_clean = data.iloc[:, 0]
    X_clean = sm.add_constant(data.iloc[:, 1:])
    fit = sm.OLS(y_clean, X_clean).fit()
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

    print(f"Panel rows: {len(panel)}")
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    main()
