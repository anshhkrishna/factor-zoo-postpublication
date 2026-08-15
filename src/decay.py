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


def randomly_signed_factor(values, block_size, rng):
    """Generate one synthetic no-edge series matched to values' volatility.

    Multiplies each contiguous block of block_size months by an independent
    +/-1 draw. This preserves the series' own volatility and short-horizon
    autocorrelation (within a block, nothing is reordered) while destroying
    any consistent directional edge across blocks, since the sign of any
    multi-block trend is randomized away.
    """
    n = len(values)
    n_blocks = -(-n // block_size)  # ceil division
    signs = rng.choice([-1.0, 1.0], size=n_blocks)
    block_signs = np.repeat(signs, block_size)[:n]
    return values * block_signs


def noise_floor_stats(dates, values, publication_year, block_size, n_draws, rng):
    """In-sample Sharpe, out-of-sample Sharpe, and ratio from n_draws
    independent randomly-signed-factor controls.

    Runs each synthetic draw through the identical in-sample/out-of-sample
    split and publication-year cutoff as decay_ratio, giving distributions a
    real factor's own in-sample Sharpe, out-of-sample Sharpe, or ratio can
    each be compared against. A factor with zero true directional edge
    produces these distributions by construction, so they are the noise
    floor.
    """
    in_sharpes = np.empty(n_draws)
    out_sharpes = np.empty(n_draws)
    ratios = np.empty(n_draws)
    for i in range(n_draws):
        synthetic = randomly_signed_factor(values, block_size, rng)
        in_sample, out_sample = split_in_out_sample(dates, synthetic, publication_year)
        in_sharpes[i] = annualized_sharpe(in_sample)
        out_sharpes[i] = annualized_sharpe(out_sample)
        ratios[i] = out_sharpes[i] / in_sharpes[i]
    return in_sharpes, out_sharpes, ratios


def noise_floor_decay_ratios(dates, values, publication_year, block_size, n_draws, rng):
    """Decay ratios from n_draws independent randomly-signed-factor controls.

    Thin wrapper around noise_floor_stats for callers that only need the
    ratio distribution.
    """
    _, _, ratios = noise_floor_stats(dates, values, publication_year, block_size, n_draws, rng)
    return ratios


def _block_partition(values, block_size):
    """Split values into contiguous, non-overlapping chunks of block_size."""
    return [values[i : i + block_size] for i in range(0, len(values), block_size)]


def block_bootstrap_sharpe(values, block_size, n_draws, rng):
    """Block-bootstrap distribution of the annualized Sharpe of one series.

    Resamples the series' own block_size-month blocks with replacement
    (drawing as many blocks as the original partition has, then trimming
    back to the original length) and recomputes annualized_sharpe on each
    resample, giving a sampling-uncertainty distribution around the point
    estimate.
    """
    blocks = _block_partition(values, block_size)
    n = len(values)
    n_blocks = len(blocks)
    sharpes = np.empty(n_draws)
    for i in range(n_draws):
        idx = rng.integers(0, n_blocks, size=n_blocks)
        resampled = np.concatenate([blocks[j] for j in idx])[:n]
        sharpes[i] = annualized_sharpe(resampled)
    return sharpes


def block_bootstrap_ratio(in_values, out_values, block_size, n_draws, rng):
    """Block-bootstrap distribution of the decay ratio.

    Resamples the in-sample and out-of-sample blocks independently on each
    draw (matching how the two halves were actually observed) and
    recomputes the ratio of their annualized Sharpes.
    """
    in_blocks = _block_partition(in_values, block_size)
    out_blocks = _block_partition(out_values, block_size)
    n_in, n_out = len(in_values), len(out_values)
    ratios = np.empty(n_draws)
    for i in range(n_draws):
        in_idx = rng.integers(0, len(in_blocks), size=len(in_blocks))
        out_idx = rng.integers(0, len(out_blocks), size=len(out_blocks))
        in_resampled = np.concatenate([in_blocks[j] for j in in_idx])[:n_in]
        out_resampled = np.concatenate([out_blocks[j] for j in out_idx])[:n_out]
        in_sharpe = annualized_sharpe(in_resampled)
        out_sharpe = annualized_sharpe(out_resampled)
        ratios[i] = out_sharpe / in_sharpe
    return ratios
