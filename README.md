# market-pipeline

A CLI data pipeline that ingests historical US market index data, flags significant price movements based on configurable thresholds, and outputs the results as a CSV.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py --config config.yaml
```

Results are written to the path specified in `output_file` in your config (default: `./results.csv`).

## Configuration

All pipeline behavior is controlled via `config.yaml`:

```yaml
data_dir: ./data            # directory containing input CSV files
output_file: ./results.csv  # path for the results CSV

checks:
  daily:
    enabled: true
    default_threshold: 0.01   # flag day-over-day changes > 1%
  weekly:
    enabled: true
    default_threshold: 0.05   # flag week-over-week changes > 5%

overrides:
  SP500:
    daily_threshold: 0.015    # SP500 daily threshold overridden to 1.5%
  DJUA:
    daily_enabled: false      # disable daily check for DJUA entirely
    weekly_enabled: false     # disable weekly check for DJUA entirely
```

- Toggle checks on/off globally with `enabled: true/false`
- Adjust default thresholds under `checks.daily` and `checks.weekly`
- Add per-ticker overrides under `overrides.<TICKER>`:
  - `daily_threshold` / `weekly_threshold` — override the threshold for that ticker
  - `daily_enabled` / `weekly_enabled` — enable or disable a specific check for that ticker

## Input Format

Place one CSV per ticker in the `data_dir` folder. The filename (without `.csv`) is used as the ticker symbol.

Each CSV must have exactly two columns:

```
observation_date,<TICKER>
2016-01-11,1923.67
2016-01-12,1938.68
```

## Data Gaps

If a value is missing for a given date, `pct_change` for that row will be `NaN` and it will be excluded from the results — no false flags are generated for missing data.

For the weekly check, if the value 5 trading days ago is missing, that comparison is also skipped. Rows are only flagged when both the current and prior values are present.

Dates that are missing entirely (i.e. the row doesn't exist in the CSV) are not interpolated or filled — the pipeline compares available rows only. This means if days are missing, the weekly check may compare across a longer window than 5 trading days. This is treated as a known limitation and noted rather than papered over with synthetic data.

## Output Format

| Column | Description |
|---|---|
| `ticker` | Ticker symbol |
| `observation_date` | Date of the flagged observation |
| `check_type` | `daily` or `weekly` |
| `value` | Price on the observation date |
| `prior_value` | Price on the comparison date |
| `prior_date` | Date of the comparison price |
| `pct_change` | Percentage change (decimal, truncated to 5 decimal places) |
| `threshold_used` | Threshold that was breached |