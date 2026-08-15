"""Publication-year decay measurement for a monthly factor return series.

Given a factor's return series and the year it was first documented in the
literature, splits the series into an in-sample window (everything through
December of that year) and an out-of-sample window (January of the
following year onward), and reports the annualized Sharpe ratio on each
side plus their ratio.
"""

import numpy as np


def annualized_sharpe(monthly_returns):
    """Annualized Sharpe ratio from monthly returns already in excess-return form."""
    mean = np.mean(monthly_returns)
    std = np.std(monthly_returns, ddof=1)
    return mean / std * np.sqrt(12)


def split_in_out_sample(dates, values, publication_year):
    """Split a dated monthly series at December of publication_year.

    In-sample is every month up to and including publication_year * 100 + 12.
    Out-of-sample is every month from (publication_year + 1) * 100 + 1 onward.
    """
    cutoff = publication_year * 100 + 12
    in_sample_mask = dates <= cutoff
    out_sample_mask = dates > cutoff
    return values[in_sample_mask], values[out_sample_mask]


def decay_ratio(dates, values, publication_year):
    """Return (in_sample_sharpe, out_sample_sharpe, decay_ratio) for one factor.

    decay_ratio is out_sample_sharpe / in_sample_sharpe. A ratio near 1 means
    no decay; a ratio near 0 or negative means the premium weakened or
    reversed after publication.
    """
    in_sample, out_sample = split_in_out_sample(dates, values, publication_year)
    in_sharpe = annualized_sharpe(in_sample)
    out_sharpe = annualized_sharpe(out_sample)
    return in_sharpe, out_sharpe, out_sharpe / in_sharpe
