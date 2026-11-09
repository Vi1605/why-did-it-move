"""Generate synthetic UK motor-insurance renewal data with a planted incident.

Planted story: from June 2025, customers on Price Comparison Websites (PCW)
receive much bigger premium increases, and the PCW share grows.
Our tool should discover this on its own.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
CHANNELS = ["Direct", "PCW", "Broker", "Telephone"]
REGIONS = ["North", "Midlands", "South East", "South West", "London", "Scotland"]
AGE_BANDS = ["18-24", "25-34", "35-49", "50-64", "65+"]
PRODUCTS = ["Comprehensive", "Third Party"]

CHANNEL_EFFECT = {"Direct": 0.2, "PCW": -0.5, "Broker": 0.4, "Telephone": 0.0}
AGE_EFFECT = {"18-24": -0.3, "25-34": 0.0, "35-49": 0.0, "50-64": 0.0, "65+": 0.3}
INCIDENT_START = pd.Timestamp("2025-06-01")


def make_month(rng, month, n):
    """Create n renewal offers for one month."""
    after = month >= INCIDENT_START
    p_channel = [0.25, 0.40, 0.20, 0.15] if after else [0.30, 0.30, 0.25, 0.15]

    channel = rng.choice(CHANNELS, n, p=p_channel)
    region = rng.choice(REGIONS, n)
    age_band = rng.choice(AGE_BANDS, n, p=[0.10, 0.25, 0.30, 0.25, 0.10])
    product = rng.choice(PRODUCTS, n, p=[0.7, 0.3])

    premium_change = rng.normal(5, 6, n)  # % price increase at renewal
    if after:  # THE INCIDENT: PCW customers get +10 points extra
        premium_change = np.where(channel == "PCW", premium_change + 10, premium_change)

    logit = (
        1.5
        - 0.09 * premium_change
        + pd.Series(channel).map(CHANNEL_EFFECT).to_numpy()
        + pd.Series(age_band).map(AGE_EFFECT).to_numpy()
    )
    p_renew = 1 / (1 + np.exp(-logit))
    renewed = (rng.random(n) < p_renew).astype(int)

    return pd.DataFrame({
        "renewal_month": month,
        "channel": channel,
        "region": region,
        "age_band": age_band,
        "product": product,
        "premium_change_pct": premium_change.round(2),
        "renewed": renewed,
    })


def main():
    rng = np.random.default_rng(SEED)
    months = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    frames = [make_month(rng, m, int(rng.normal(8000, 300))) for m in months]
    df = pd.concat(frames, ignore_index=True)
    df.insert(0, "policy_id", np.arange(1, len(df) + 1))
    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/renewals.csv", index=False)
    print(f"Saved {len(df):,} rows to data/renewals.csv")


if __name__ == "__main__":
    main()

    