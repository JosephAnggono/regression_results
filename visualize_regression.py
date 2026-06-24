"""Scatter plots and fit-shape comparison for SCMP regression panel."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from regression_lib import ANALYSIS_COLS, PREDICTORS, TRAFFIC_COLS, build_panel

REPO = Path(__file__).resolve().parent
OUT = REPO / "output_regression"
FIG = OUT / "figures"

LABELS = {
    "quality_index": "Quality index (weekly mean ARQI)",
    "political_score": "Political score (pro-Beijing balance)",
    "visits": "Visits",
    "unique_visitors": "Unique visitors",
    "total_pages": "Total pages",
    "total_time_hours": "Total time (hours)",
}


def r_squared(y: np.ndarray, y_hat: np.ndarray) -> float:
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot else 0.0


def fit_shapes(x: np.ndarray, y: np.ndarray) -> dict:
    pearson = float(np.corrcoef(x, y)[0, 1])
    spearman = float(pd.Series(x).corr(pd.Series(y), method="spearman"))

    coef_lin = np.polyfit(x, y, 1)
    y_lin = np.polyval(coef_lin, x)
    r2_lin = r_squared(y, y_lin)

    coef_poly2 = np.polyfit(x, y, 2)
    y_poly2 = np.polyval(coef_poly2, x)
    r2_poly2 = r_squared(y, y_poly2)

    coef_poly3 = np.polyfit(x, y, 3)
    y_poly3 = np.polyval(coef_poly3, x)
    r2_poly3 = r_squared(y, y_poly3)

    fits = {"linear": r2_lin, "polynomial_deg2": r2_poly2, "polynomial_deg3": r2_poly3}
    best = max(fits, key=fits.get)
    return {
        "pearson_r": pearson,
        "spearman_r": spearman,
        "r2_linear": r2_lin,
        "r2_poly2": r2_poly2,
        "r2_poly3": r2_poly3,
        "best_fit": best,
        "best_r2": fits[best],
        "_coef_lin": coef_lin,
        "_coef_poly2": coef_poly2,
        "_coef_poly3": coef_poly3,
    }


def plot_scatter_with_fits(x_col: str, y_col: str, panel: pd.DataFrame) -> None:
    x = panel[x_col].to_numpy(dtype=float)
    y = panel[y_col].to_numpy(dtype=float)
    info = fit_shapes(x, y)

    xs = np.linspace(x.min(), x.max(), 200)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x, y, alpha=0.45, s=28, edgecolors="none", color="#2980b9")
    ax.plot(xs, np.polyval(info["_coef_lin"], xs), "--", color="#e74c3c", lw=2, label=f"Linear (R²={info['r2_linear']:.3f})")
    ax.plot(xs, np.polyval(info["_coef_poly2"], xs), "-", color="#27ae60", lw=2, label=f"Poly² (R²={info['r2_poly2']:.3f})")
    ax.plot(xs, np.polyval(info["_coef_poly3"], xs), ":", color="#8e44ad", lw=2, label=f"Poly³ (R²={info['r2_poly3']:.3f})")
    ax.set_xlabel(LABELS.get(x_col, x_col))
    ax.set_ylabel(LABELS.get(y_col, y_col))
    ax.set_title(
        f"{LABELS.get(y_col, y_col)} vs {LABELS.get(x_col, x_col)}\n"
        f"Pearson r={info['pearson_r']:.3f} | Spearman ρ={info['spearman_r']:.3f} | Best: {info['best_fit']}"
    )
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / f"scatter_{y_col}_vs_{x_col}.png", dpi=150)
    plt.close(fig)

    return info


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    panel = build_panel()

    sns.set_theme(style="whitegrid", font_scale=0.95)

    for method, fname in [("pearson", "correlation_heatmap_pearson.png"), ("spearman", "correlation_heatmap_spearman.png")]:
        corr = panel[ANALYSIS_COLS].corr(method=method)
        corr.index = [LABELS.get(c, c) for c in corr.index]
        corr.columns = [LABELS.get(c, c) for c in corr.columns]
        fig, ax = plt.subplots(figsize=(8, 6.5))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax, square=True)
        ax.set_title(f"{method.title()} correlation — SCMP weekly panel (2018–2024)")
        fig.tight_layout()
        fig.savefig(FIG / fname, dpi=150)
        plt.close(fig)

    rows = []
    for x_col in PREDICTORS:
        for y_col in TRAFFIC_COLS:
            info = plot_scatter_with_fits(x_col, y_col, panel)
            rows.append({"x": x_col, "y": y_col, **{k: v for k, v in info.items() if not k.startswith("_")}})

    pd.DataFrame(rows).to_csv(OUT / "fit_shape_comparison.csv", index=False)

    fig, axes = plt.subplots(len(TRAFFIC_COLS), len(PREDICTORS), figsize=(11, 13))
    for i, y_col in enumerate(TRAFFIC_COLS):
        for j, x_col in enumerate(PREDICTORS):
            ax = axes[i, j]
            x = panel[x_col].to_numpy(dtype=float)
            y = panel[y_col].to_numpy(dtype=float)
            info = fit_shapes(x, y)
            xs = np.linspace(x.min(), x.max(), 100)
            ax.scatter(x, y, alpha=0.35, s=14, color="#2980b9")
            ax.plot(xs, np.polyval(info["_coef_lin"], xs), "--", color="#e74c3c", lw=1.2)
            ax.plot(xs, np.polyval(info["_coef_poly2"], xs), "-", color="#27ae60", lw=1.2)
            ax.set_title(f"r={info['pearson_r']:.2f} | best={info['best_fit']}", fontsize=9)
            if i == len(TRAFFIC_COLS) - 1:
                ax.set_xlabel(LABELS.get(x_col, x_col), fontsize=8)
            if j == 0:
                ax.set_ylabel(LABELS.get(y_col, y_col), fontsize=8)
    fig.suptitle("Predictors vs traffic (red=linear, green=poly²)", fontsize=12, y=1.01)
    fig.tight_layout()
    fig.savefig(FIG / "scatter_grid_all.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved figures to {FIG}")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
