"""Publication-year decay for the five tested factors.

For each factor, computes the real decay ratio (out-of-sample Sharpe over
in-sample Sharpe, split at the factor's publication year) and compares it
against a randomly-signed-factor noise floor (the 2.5th/97.5th percentile
of decay ratios from series with the same volatility but no true edge) and
the market/FF3 placebo ratios over the identical window.
"""

import time

import numpy as np

import baseline
import data
import decay

PUBLICATION_YEARS = baseline.PUBLICATION_YEARS

# Which loader supplies each tested factor's own series, keyed by the
# column name that loader returns for it.
_LOADER = {
    "SMB": data.load_three_factor,
    "HML": data.load_three_factor,
    "Mom": data.load_momentum,
    "RMW": data.load_five_factor,
    "CMA": data.load_five_factor,
}

BLOCK_SIZE = 12
N_DRAWS = 1000
SEED = 20260815


def run():
    rng = np.random.default_rng(SEED)
    three_factor = data.load_three_factor()
    tilt = baseline.ff3_tilt(three_factor)

    print("factor-zoo-postpublication: publication-year decay experiment")
    print(f"seed={SEED} block_size={BLOCK_SIZE} n_draws={N_DRAWS}")
    print()
    header = (
        f"{'factor':<8}{'pub_year':>10}{'in_sharpe':>12}{'out_sharpe':>12}"
        f"{'ratio':>10}{'noise_p2.5':>12}{'noise_p97.5':>12}"
        f"{'mkt_ratio':>12}{'ff3_ratio':>12}"
    )
    print(header)
    for name, publication_year in PUBLICATION_YEARS.items():
        series = _LOADER[name]()
        dates, values = series["dates"], series[name]
        in_sharpe, out_sharpe, ratio = decay.decay_ratio(dates, values, publication_year)
        noise_ratios = decay.noise_floor_decay_ratios(
            dates, values, publication_year, BLOCK_SIZE, N_DRAWS, rng
        )
        p2_5, p97_5 = np.percentile(noise_ratios, [2.5, 97.5])

        mkt_dates, mkt_values = baseline.restrict_to_dates(
            three_factor["dates"], three_factor["Mkt-RF"], dates
        )
        _, _, mkt_ratio = decay.decay_ratio(mkt_dates, mkt_values, publication_year)
        tilt_dates, tilt_values = baseline.restrict_to_dates(three_factor["dates"], tilt, dates)
        _, _, ff3_ratio = decay.decay_ratio(tilt_dates, tilt_values, publication_year)

        print(
            f"{name:<8}{publication_year:>10}{in_sharpe:>12.3f}{out_sharpe:>12.3f}"
            f"{ratio:>10.3f}{p2_5:>12.3f}{p97_5:>12.3f}"
            f"{mkt_ratio:>12.3f}{ff3_ratio:>12.3f}"
        )


if __name__ == "__main__":
    start = time.perf_counter()
    run()
    elapsed = time.perf_counter() - start
    print()
    print(f"elapsed: {elapsed:.2f}s")
