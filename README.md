# regression_results

Weekly OLS regression for **HKFP, SCMP, AM730**: ads and traffic vs quality index and political score.

## Setup

```bash
pip install -r requirements.txt
```

Put input files in `data/` (see `data/README.md`). Then:

```bash
python run_regression_analysis.py
```

## Outputs

`output_regression/` — `weekly_panel.csv`, `ols_results.csv`, `correlations.csv`

## Docs

See `regression_task_notes.md` for models, data gaps, and what to report.

**Note:** GitHub stores code + results. Re-run the script locally after pulling; it does not run automatically on push.
