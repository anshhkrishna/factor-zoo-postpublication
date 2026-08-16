"""Parsers for the Ken French data library CSVs vendored under data/ken-french/.

Each loader reads one monthly table: a prose header block, a header row that
starts with a comma, monthly rows keyed by a YYYYMM date, then a blank line.
Values are returned in the file's native units (percent, not decimal) and
missing-value codes (-99.99, -999) are converted to NaN.
"""

import os

import numpy as np

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ken-french")

THREE_FACTOR_PATH = os.path.join(_DATA_DIR, "F-F_Research_Data_Factors.csv")
FIVE_FACTOR_PATH = os.path.join(_DATA_DIR, "F-F_Research_Data_5_Factors_2x3.csv")
MOMENTUM_PATH = os.path.join(_DATA_DIR, "F-F_Momentum_Factor.csv")
PORTFOLIOS_25_PATH = os.path.join(_DATA_DIR, "25_Portfolios_5x5.csv")

_MISSING_CODES = (-99.99, -999.0)


def _parse_monthly_table(lines, header_idx):
    columns = [c.strip() for c in lines[header_idx].split(",")[1:]]
    dates = []
    rows = []
    for line in lines[header_idx + 1 :]:
        if line.strip() == "":
            break
        fields = line.split(",")
        date_field = fields[0].strip()
        if not (date_field.isdigit() and len(date_field) == 6):
            break
        dates.append(int(date_field))
        rows.append([float(v) for v in fields[1:]])
    dates_arr = np.array(dates, dtype=np.int64)
    data_arr = np.array(rows, dtype=np.float64)
    for code in _MISSING_CODES:
        data_arr[data_arr == code] = np.nan
    return dates_arr, columns, data_arr


def _load_first_table(path):
    with open(path, newline="") as f:
        lines = [line.rstrip("\r\n") for line in f]
    header_idx = next(i for i, line in enumerate(lines) if line.startswith(","))
    dates, columns, data = _parse_monthly_table(lines, header_idx)
    series = {"dates": dates}
    for i, col in enumerate(columns):
        series[col] = data[:, i]
    return series


def load_three_factor(path=THREE_FACTOR_PATH):
    """Monthly Mkt-RF, SMB, HML, RF, 1926-07 onward."""
    return _load_first_table(path)


def load_five_factor(path=FIVE_FACTOR_PATH):
    """Monthly Mkt-RF, SMB, HML, RMW, CMA, RF, 1963-07 onward."""
    return _load_first_table(path)


def load_momentum(path=MOMENTUM_PATH):
    """Monthly Mom, 1927-01 onward."""
    return _load_first_table(path)


def load_25_portfolios(path=PORTFOLIOS_25_PATH):
    """First section only: average value-weighted monthly returns, 25 size/BM portfolios."""
    return _load_first_table(path)
