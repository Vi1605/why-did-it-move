import numpy as np
import pandas as pd


def detect_anomalies(monthly, col="renewal_rate", window=6, threshold=3.0):
    """Flag months whose value is unusual versus the previous `window` months."""
    out = monthly.copy()
    past = out[col].shift(1).rolling(window)  # shift(1): only look at the past
    median = past.median()
    mad = past.apply(lambda s: np.median(np.abs(s - np.median(s))), raw=True)
    scale = np.maximum(1.4826 * mad, 0.003)  # floor stops divide-by-tiny-number
    out["robust_z"] = (out[col] - median) / scale
    out["is_anomaly"] = out["robust_z"].abs() > threshold
    return out
