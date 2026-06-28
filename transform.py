import pandas as pd


def apply_checks(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    try:
        checks = config["checks"]
    except KeyError:
        raise KeyError("Config is missing required 'checks' section")

    overrides = config.get("overrides", {})

    df = df.sort_values(["ticker", "observation_date"]).reset_index(drop=True)

    df["daily_pct_change"] = df.groupby("ticker")["value"].pct_change(1)
    df["weekly_pct_change"] = df.groupby("ticker")["value"].pct_change(5)
    df["prior_value_daily"] = df.groupby("ticker")["value"].shift(1)
    df["prior_value_weekly"] = df.groupby("ticker")["value"].shift(5)
    df["prior_date_daily"] = df.groupby("ticker")["observation_date"].shift(1)
    df["prior_date_weekly"] = df.groupby("ticker")["observation_date"].shift(5)

    results = []

    for ticker, group in df.groupby("ticker"):
        ticker_override = overrides.get(ticker, {})

        daily_enabled = ticker_override.get("daily_enabled", checks["daily"]["enabled"])
        if daily_enabled:
            threshold = ticker_override.get("daily_threshold", checks["daily"]["default_threshold"])
            flagged = group[group["daily_pct_change"].abs() > threshold].copy()
            flagged["check_type"] = "daily"
            flagged["threshold_used"] = threshold
            flagged["prior_value"] = flagged["prior_value_daily"]
            flagged["prior_date"] = flagged["prior_date_daily"]
            flagged["pct_change"] = flagged["daily_pct_change"]
            results.append(flagged)

        weekly_enabled = ticker_override.get("weekly_enabled", checks["weekly"]["enabled"])
        if weekly_enabled:
            threshold = ticker_override.get("weekly_threshold", checks["weekly"]["default_threshold"])
            flagged = group[group["weekly_pct_change"].abs() > threshold].copy()
            flagged["check_type"] = "weekly"
            flagged["threshold_used"] = threshold
            flagged["prior_value"] = flagged["prior_value_weekly"]
            flagged["prior_date"] = flagged["prior_date_weekly"]
            flagged["pct_change"] = flagged["weekly_pct_change"]
            results.append(flagged)

    if not results:
        return pd.DataFrame()

    try:
        output_cols = ["ticker", "observation_date", "check_type", "value", "prior_value", "prior_date", "pct_change", "threshold_used"]
        final = pd.concat(results, ignore_index=True)[output_cols]
        final["pct_change"] = (final["pct_change"] * 100000).astype(int) / 100000
        return final
    except Exception as e:
        raise RuntimeError(f"Failed to build results DataFrame: {e}")
