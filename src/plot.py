"""Headline chart for the publication-year decay comparison.

Reads the committed run logs (results/run.log, results/rigor.log,
results/baseline.log) and regenerates results/headline.png: for each of the
five tested factors, in-sample Sharpe next to out-of-sample Sharpe (with the
out-of-sample bar's error bar showing the randomly-signed-factor noise
floor's 95% range from the rigor log), plus the Mkt-RF and FF3 placebo
out-of-sample Sharpes over the same window. Nothing here is computed fresh;
every number plotted is parsed from a log already on disk.
"""

import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
RUN_LOG = os.path.join(_RESULTS_DIR, "run.log")
RIGOR_LOG = os.path.join(_RESULTS_DIR, "rigor.log")
BASELINE_LOG = os.path.join(_RESULTS_DIR, "baseline.log")
OUTPUT_PATH = os.path.join(_RESULTS_DIR, "headline.png")

FACTOR_ORDER = ["SMB", "HML", "Mom", "RMW", "CMA"]

COLOR_IN_SAMPLE = "#2a78d6"
COLOR_OUT_SAMPLE = "#eb6834"
COLOR_MKT = "#1baf7a"
COLOR_FF3 = "#eda100"
COLOR_INK = "#0b0b0b"
COLOR_MUTED = "#898781"
COLOR_GRID = "#e1e0d9"


def parse_run_log(path):
    """factor -> (in_sharpe, out_sharpe) from the experiment log."""
    out = {}
    pattern = re.compile(
        r"^(SMB|HML|Mom|RMW|CMA)\s+(\d+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)"
    )
    with open(path) as f:
        for line in f:
            m = pattern.match(line)
            if m:
                name, _, in_sharpe, out_sharpe, _ = m.groups()
                out[name] = (float(in_sharpe), float(out_sharpe))
    return out


def parse_rigor_log(path):
    """factor -> (noise_lo, noise_hi) out-of-sample Sharpe range."""
    out = {}
    pattern = re.compile(
        r"^(SMB|HML|Mom|RMW|CMA)\s+[\-\d.]+\s+(?:True|False)\s+[\-\d.]+\s+"
        r"\[([\-\d.]+),([\-\d.]+)\]"
    )
    with open(path) as f:
        for line in f:
            m = pattern.match(line)
            if m:
                name, lo, hi = m.groups()
                out[name] = (float(lo), float(hi))
    return out


def parse_baseline_log(path):
    """factor -> {"Mkt-RF": out_sharpe, "FF3": out_sharpe} placebo values."""
    out = {name: {} for name in FACTOR_ORDER}
    pattern = re.compile(
        r"^(Mkt-RF|FF3)\s+(\d+)\s+([\-\d.]+)\s+([\-\d.]+)\s+([\-\d.]+)\s+"
        r"\(placebo for (SMB|HML|Mom|RMW|CMA),"
    )
    with open(path) as f:
        for line in f:
            m = pattern.match(line)
            if m:
                placebo, _, _, out_sharpe, _, factor = m.groups()
                out[factor][placebo] = float(out_sharpe)
    return out


def build_chart(run_data, rigor_data, baseline_data, output_path):
    n = len(FACTOR_ORDER)
    bar_width = 0.2
    positions = range(n)

    in_vals = [run_data[f][0] for f in FACTOR_ORDER]
    out_vals = [run_data[f][1] for f in FACTOR_ORDER]
    noise_lo = [rigor_data[f][0] for f in FACTOR_ORDER]
    noise_hi = [rigor_data[f][1] for f in FACTOR_ORDER]
    out_err_lo = [max(0.0, o - lo) for o, lo in zip(out_vals, noise_lo)]
    out_err_hi = [max(0.0, hi - o) for o, hi in zip(out_vals, noise_hi)]
    mkt_vals = [baseline_data[f]["Mkt-RF"] for f in FACTOR_ORDER]
    ff3_vals = [baseline_data[f]["FF3"] for f in FACTOR_ORDER]

    plt.rcParams.update({"font.size": 12, "font.family": "sans-serif"})
    fig, ax = plt.subplots(figsize=(1600 / 150, 900 / 150), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    offsets = [-1.5 * bar_width, -0.5 * bar_width, 0.5 * bar_width, 1.5 * bar_width]
    x = [p + offsets[0] for p in positions]
    ax.bar(x, in_vals, width=bar_width, color=COLOR_IN_SAMPLE, label="in-sample Sharpe")

    x = [p + offsets[1] for p in positions]
    ax.bar(
        x,
        out_vals,
        width=bar_width,
        color=COLOR_OUT_SAMPLE,
        label="out-of-sample Sharpe",
        yerr=[out_err_lo, out_err_hi],
        capsize=4,
        ecolor=COLOR_INK,
        error_kw={"elinewidth": 1.2, "alpha": 0.7},
    )

    x = [p + offsets[2] for p in positions]
    ax.bar(x, mkt_vals, width=bar_width, color=COLOR_MKT, label="Mkt-RF placebo (out-of-sample)")

    x = [p + offsets[3] for p in positions]
    ax.bar(x, ff3_vals, width=bar_width, color=COLOR_FF3, label="FF3 tilt placebo (out-of-sample)")

    ax.axhline(0, color=COLOR_MUTED, linewidth=0.8)
    ax.set_xticks(list(positions))
    ax.set_xticklabels(FACTOR_ORDER)
    ax.set_ylabel("annualized Sharpe ratio")
    ax.set_title(
        "post-publication sharpe falls into the no-edge noise floor;\n"
        "the market and ff3 tilt do not decay the same way",
        fontsize=14,
        color=COLOR_INK,
    )
    ax.grid(axis="y", color=COLOR_GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=COLOR_INK)
    ax.legend(loc="upper left", frameon=False, fontsize=11)

    fig.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    run_data = parse_run_log(RUN_LOG)
    rigor_data = parse_rigor_log(RIGOR_LOG)
    baseline_data = parse_baseline_log(BASELINE_LOG)
    missing = [f for f in FACTOR_ORDER if f not in run_data or f not in rigor_data]
    if missing:
        raise RuntimeError(f"could not parse log entries for: {missing}")
    build_chart(run_data, rigor_data, baseline_data, OUTPUT_PATH)
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
