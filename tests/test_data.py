import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import data  # noqa: E402

LAST_MONTH = 202606


def test_three_factor_date_range():
    series = data.load_three_factor()
    assert series["dates"][0] == 192607
    assert series["dates"][-1] == LAST_MONTH


def test_momentum_date_range():
    series = data.load_momentum()
    assert series["dates"][0] == 192701
    assert series["dates"][-1] == LAST_MONTH


def test_five_factor_date_range():
    series = data.load_five_factor()
    assert series["dates"][0] == 196307
    assert series["dates"][-1] == LAST_MONTH


def test_dates_strictly_increasing():
    for loader in (
        data.load_three_factor,
        data.load_five_factor,
        data.load_momentum,
        data.load_25_portfolios,
    ):
        dates = loader()["dates"]
        assert np.all(np.diff(dates) > 0)


def test_no_missing_value_codes_remain():
    for loader in (
        data.load_three_factor,
        data.load_five_factor,
        data.load_momentum,
        data.load_25_portfolios,
    ):
        series = loader()
        for name, values in series.items():
            if name == "dates":
                continue
            assert not np.isnan(values).any(), f"unexpected NaN in {name}"
            assert not np.any(values == -99.99), f"unconverted missing code in {name}"
            assert not np.any(values == -999.0), f"unconverted missing code in {name}"


def test_25_portfolios_value_spread_tracks_hml():
    """A hand-built value-minus-growth spread from the 25 portfolios should
    track the official HML series, confirming the parser reads the columns
    it claims to. Averaged across all five size quintiles rather than just
    the size extremes: the two-corner spread (SMALL/BIG only) correlates at
    only r=0.66, since a single quintile's BM-extreme portfolio is far
    noisier than HML's own tercile-based construction. Averaging over all
    five quintiles cancels much of that size-specific noise.
    """
    portfolios = data.load_25_portfolios()
    three_factor = data.load_three_factor()

    high_bm_cols = ["SMALL HiBM", "ME2 BM5", "ME3 BM5", "ME4 BM5", "BIG HiBM"]
    low_bm_cols = ["SMALL LoBM", "ME2 BM1", "ME3 BM1", "ME4 BM1", "BIG LoBM"]
    high_bm = np.mean([portfolios[c] for c in high_bm_cols], axis=0)
    low_bm = np.mean([portfolios[c] for c in low_bm_cols], axis=0)
    spread = high_bm - low_bm

    common_dates = np.intersect1d(portfolios["dates"], three_factor["dates"])
    spread_idx = np.searchsorted(portfolios["dates"], common_dates)
    hml_idx = np.searchsorted(three_factor["dates"], common_dates)

    r = np.corrcoef(spread[spread_idx], three_factor["HML"][hml_idx])[0, 1]
    assert r > 0.8
