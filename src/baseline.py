"""Placebo baseline: publication-year Sharpe split on series that were never
"published" as anomalies.

Runs the same in-sample/out-of-sample split from decay.py on the market
factor (Mkt-RF) and an equal-weight Mkt-RF/SMB/HML tilt (FF3), at each of
the five publication years used for the tested factors, over the same
date range that factor is actually available in. If these never-published
series show as much apparent decay as a tested factor over the identical
window, that factor's decay is not attributable to publication, it is just
what any two multi-decade windows look like.
"""

import numpy as np

import data
import decay

PUBLICATION_YEARS = {
    "SMB": 1992,
    "HML": 1992,
    "Mom": 1993,
    "RMW": 2013,
    "CMA": 2008,
}

# Which loader supplies each tested factor's own date range, so the placebo
# is restricted to the same window the tested factor is actually available in.
_AVAILABILITY_LOADER = {
    "SMB": data.load_three_factor,
    "HML": data.load_three_factor,
    "Mom": data.load_momentum,
    "RMW": data.load_five_factor,
    "CMA": data.load_five_factor,
}


def ff3_tilt(three_factor):
    """Equal-weight combination of Mkt-RF, SMB, HML."""
    return (three_factor["Mkt-RF"] + three_factor["SMB"] + three_factor["HML"]) / 3.0


def restrict_to_dates(dates, values, target_dates):
    """Select the subset of (dates, values) whose dates appear in target_dates."""
    mask = np.isin(dates, target_dates)
    return dates[mask], values[mask]


def run():
    three_factor = data.load_three_factor()
    tilt = ff3_tilt(three_factor)

    print("factor-zoo-postpublication: baseline placebo")
    print("Series that were never published as anomalies, split at the same")
    print("publication years used for the tested factors, restricted to each")
    print("factor's own date range. Decay here reflects only the fact that")
    print("different multi-decade windows differ, not any publication effect.")
    print()
    header = f"{'placebo':<10}{'pub_year':>10}{'in_sharpe':>12}{'out_sharpe':>12}{'ratio':>10}"
    print(header)
    for name, publication_year in PUBLICATION_YEARS.items():
        target_dates = _AVAILABILITY_LOADER[name]()["dates"]
        mkt_dates, mkt_values = restrict_to_dates(
            three_factor["dates"], three_factor["Mkt-RF"], target_dates
        )
        tilt_dates, tilt_values = restrict_to_dates(three_factor["dates"], tilt, target_dates)

        in_sharpe, out_sharpe, ratio = decay.decay_ratio(mkt_dates, mkt_values, publication_year)
        print(
            f"{'Mkt-RF':<10}{publication_year:>10}{in_sharpe:>12.3f}"
            f"{out_sharpe:>12.3f}{ratio:>10.3f}   (placebo for {name}, "
            f"{target_dates[0]}-{target_dates[-1]})"
        )
        in_sharpe, out_sharpe, ratio = decay.decay_ratio(tilt_dates, tilt_values, publication_year)
        print(
            f"{'FF3':<10}{publication_year:>10}{in_sharpe:>12.3f}"
            f"{out_sharpe:>12.3f}{ratio:>10.3f}   (placebo for {name}, "
            f"{target_dates[0]}-{target_dates[-1]})"
        )


if __name__ == "__main__":
    run()
