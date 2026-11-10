import numpy as np
import pandas as pd

from src.generate_data import make_month
from src.rca import contribution_analysis, run_rca, total_change


def _month(m, a_n, a_ren, b_n, b_ren):
    return pd.DataFrame({
        "renewal_month": [pd.Timestamp(m)] * (a_n + b_n),
        "channel": ["A"] * a_n + ["B"] * b_n,
        "renewed": [1] * a_ren + [0] * (a_n - a_ren) + [1] * b_ren + [0] * (b_n - b_ren),
    })


def test_contributions_add_up_to_total_change():
    df = pd.concat([_month("2025-01-01", 50, 40, 50, 30),
                    _month("2025-02-01", 40, 32, 60, 24)])
    res = contribution_analysis(df, "channel", "2025-01-01", "2025-02-01")
    expected = total_change(df, "2025-01-01", "2025-02-01")
    assert abs(res["contribution"].sum() - expected) < 1e-9


def test_finds_the_planted_driver():
    rng = np.random.default_rng(1)
    df = pd.concat([
        make_month(rng, pd.Timestamp("2025-05-01"), 8000),
        make_month(rng, pd.Timestamp("2025-06-01"), 8000),
    ])
    top = run_rca(df, "2025-05-01", "2025-06-01").iloc[0]
    assert top["segment"] == "PCW"
    