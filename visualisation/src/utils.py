import hashlib
from math import trunc

import pandas as pd
import scipy.stats as st


def create_hash(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def format_string(s: str) -> str:
    """Format a string to be more readable."""
    return s.replace("_", " ").title()


def mean_ci(series: pd.Series, confidence: float = 0.95):
    n = len(series)
    mean = series.mean()
    sem = series.std(ddof=1) / (n**0.5)
    h = sem * st.t.ppf((1 + confidence) / 2, n - 1)
    return trunc(mean), trunc(h)
