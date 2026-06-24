"""Shared SCMP weekly panel loaders (2018–2024)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"

YEAR_MIN, YEAR_MAX = 2018, 2024

POLITICAL_CSV = DATA / "political_score_weekly.csv"
QUALITY_CSV = DATA / "quality_index.csv"
TRAFFIC_XLSX = DATA / "SCMP_hk_marketshare.xlsx"

POLITICAL_KEY = "south_china_morning_post"
QUALITY_KEY = "south_china_morning_post"

TRAFFIC_COLS = {
    "visits": "Visits",
    "unique_visitors": "Unique Visitors",
    "total_pages": "Estimated Total Pages",
    "total_time_hours": "Estimated Total Time Hours",
}

PREDICTORS = ["quality_index", "political_score"]
ANALYSIS_COLS = PREDICTORS + list(TRAFFIC_COLS.keys())


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


def load_traffic() -> pd.DataFrame:
    ws = pd.read_excel(TRAFFIC_XLSX, sheet_name="Weekly Summary", header=2)
    hk = ws[ws["Region"] == "Hong Kong"].copy()
    hk["week"] = iso_week(hk["Week Start"])
    hk = hk[(week_year(hk["week"]) >= YEAR_MIN) & (week_year(hk["week"]) <= YEAR_MAX)]
    keep = ["week"] + list(TRAFFIC_COLS.values())
    return hk[keep].rename(columns={v: k for k, v in TRAFFIC_COLS.items()})


def build_panel() -> pd.DataFrame:
    panel = load_traffic()
    panel = panel.merge(load_political(), on="week", how="inner")
    panel = panel.merge(load_quality(), on="week", how="inner")
    return panel.sort_values("week").reset_index(drop=True)
