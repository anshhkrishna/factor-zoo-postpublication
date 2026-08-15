"""Rigor checks on the publication-year decay comparison.

For each of the five tested factors this adds three things beyond the raw
decay-ratio experiment: a block-bootstrap confidence interval on the
out-of-sample Sharpe and on the decay ratio (sampling uncertainty around the
observed point estimate), a comparison of the average real decay ratio
against the pooled noise-floor ratio distribution, and a comparison of each
factor's own out-of-sample Sharpe against a noise floor built from
out-of-sample Sharpes of the same randomly-signed synthetic controls.

The last comparison, not the ratio one, is what decides "does not survive
publication" here. A decay ratio is a quotient of two Sharpes, and when a
synthetic no-edge series happens to land an in-sample Sharpe near zero the
ratio blows up in either direction -- the noise floor for the ratio is so
wide that almost nothing ever falls outside its 95% range, which makes an
outside-the-range test on the ratio close to uninformative. Comparing the
out-of-sample Sharpe itself against a noise floor of out-of-sample Sharpes
avoids that quotient blowup and is a direct test of the claim as stated:
whether the post-publication premium is distinguishable from a no-edge
control of matched volatility.
"""

import time

import numpy as np

import baseline
import data
import decay
import experiment

PUBLICATION_YEARS = baseline.PUBLICATION_YEARS
_LOADER = experiment._LOADER

BLOCK_SIZE = experiment.BLOCK_SIZE
N_DRAWS = experiment.N_DRAWS
NOISE_SEED = experiment.SEED
BOOTSTRAP_SEED = 20260816


def run():
    noise_rng = np.random.default_rng(NOISE_SEED)
    bootstrap_rng = np.random.default_rng(BOOTSTRAP_SEED)

    print("factor-zoo-postpublication: rigor checks on the decay comparison")
    print(
        f"noise_seed={NOISE_SEED} bootstrap_seed={BOOTSTRAP_SEED} "
        f"block_size={BLOCK_SIZE} n_draws={N_DRAWS}"
    )
    print()

    real_ratios = {}
    pooled_noise_ratios = []
    rows = []
    for name, publication_year in PUBLICATION_YEARS.items():
        series = _LOADER[name]()
        dates, values = series["dates"], series[name]
        in_sample, out_sample = decay.split_in_out_sample(dates, values, publication_year)
        in_sharpe, out_sharpe, ratio = decay.decay_ratio(dates, values, publication_year)
        real_ratios[name] = ratio

        noise_in, noise_out, noise_ratio = decay.noise_floor_stats(
            dates, values, publication_year, BLOCK_SIZE, N_DRAWS, noise_rng
        )
        pooled_noise_ratios.append(noise_ratio)
        noise_out_p2_5, noise_out_p97_5 = np.percentile(noise_out, [2.5, 97.5])
        noise_ratio_p2_5, noise_ratio_p97_5 = np.percentile(noise_ratio, [2.5, 97.5])

        boot_out_sharpe = decay.block_bootstrap_sharpe(
            out_sample, BLOCK_SIZE, N_DRAWS, bootstrap_rng
        )
        boot_out_p2_5, boot_out_p97_5 = np.percentile(boot_out_sharpe, [2.5, 97.5])

        boot_ratio = decay.block_bootstrap_ratio(
            in_sample, out_sample, BLOCK_SIZE, N_DRAWS, bootstrap_rng
        )
        boot_ratio_p2_5, boot_ratio_p97_5 = np.percentile(boot_ratio, [2.5, 97.5])

        ratio_outside_noise = ratio < noise_ratio_p2_5 or ratio > noise_ratio_p97_5
        sharpe_indistinguishable_from_noise = noise_out_p2_5 <= out_sharpe <= noise_out_p97_5

        rows.append(
            (
                name,
                publication_year,
                out_sharpe,
                boot_out_p2_5,
                boot_out_p97_5,
                ratio,
                boot_ratio_p2_5,
                boot_ratio_p97_5,
                noise_out_p2_5,
                noise_out_p97_5,
                ratio_outside_noise,
                sharpe_indistinguishable_from_noise,
            )
        )

    print("Block-bootstrap CIs (resampling the factor's own observed blocks with")
    print("replacement -- sampling uncertainty around the point estimate):")
    print()
    header = (
        f"{'factor':<8}{'out_sharpe':>12}{'ci_lo':>10}{'ci_hi':>10}"
        f"{'ratio':>10}{'ratio_ci_lo':>13}{'ratio_ci_hi':>13}"
    )
    print(header)
    for row in rows:
        name, pub_year, out_sharpe = row[0], row[1], row[2]
        boot_out_p2_5, boot_out_p97_5 = row[3], row[4]
        ratio, boot_ratio_p2_5, boot_ratio_p97_5 = row[5], row[6], row[7]
        print(
            f"{name:<8}{out_sharpe:>12.3f}{boot_out_p2_5:>10.3f}{boot_out_p97_5:>10.3f}"
            f"{ratio:>10.3f}{boot_ratio_p2_5:>13.3f}{boot_ratio_p97_5:>13.3f}"
        )
    print()

    print("Noise-floor comparisons (randomly-signed synthetic controls, matched")
    print("volatility, zero true edge -- same draws used in the decay experiment log):")
    print()
    header = (
        f"{'factor':<8}{'ratio':>10}{'ratio_outside_range':>22}"
        f"{'out_sharpe':>12}{'noise_sharpe_range':>22}{'indistinguishable':>20}"
    )
    print(header)
    for row in rows:
        (
            name,
            pub_year,
            out_sharpe,
            _,
            _,
            ratio,
            _,
            _,
            noise_out_p2_5,
            noise_out_p97_5,
            ratio_outside_noise,
            sharpe_indistinguishable,
        ) = row
        noise_sharpe_range = f"[{noise_out_p2_5:.3f},{noise_out_p97_5:.3f}]"
        print(
            f"{name:<8}{ratio:>10.3f}{str(ratio_outside_noise):>22}"
            f"{out_sharpe:>12.3f}{noise_sharpe_range:>22}{str(sharpe_indistinguishable):>20}"
        )
    print()

    avg_real_ratio = np.mean(list(real_ratios.values()))
    pooled = np.concatenate(pooled_noise_ratios)
    pooled_p2_5, pooled_p97_5 = np.percentile(pooled, [2.5, 97.5])
    percentile_rank = 100.0 * np.mean(pooled < avg_real_ratio)
    print(
        f"average real decay ratio across the five factors: {avg_real_ratio:.3f}"
    )
    print(
        f"pooled noise-floor ratio distribution (5x{N_DRAWS} draws) "
        f"[p2.5, p97.5]: [{pooled_p2_5:.3f}, {pooled_p97_5:.3f}]"
    )
    print(
        f"average real ratio sits at the {percentile_rank:.1f}th percentile of "
        "the pooled noise floor "
        f"({'inside' if pooled_p2_5 <= avg_real_ratio <= pooled_p97_5 else 'outside'} "
        "the 95% range)"
    )
    print()

    n_ratio_outside = sum(row[10] for row in rows)
    n_sharpe_indistinguishable = sum(row[11] for row in rows)
    print(
        f"{n_ratio_outside}/5 factors have a decay ratio outside their own noise "
        "floor's 95% range (see the module docstring for why this framing is "
        "close to uninformative here)"
    )
    print(
        f"{n_sharpe_indistinguishable}/5 factors have an out-of-sample Sharpe "
        "statistically indistinguishable from a no-edge noise floor of matched "
        "volatility -- this is the comparison used for the core-claim test"
    )


if __name__ == "__main__":
    start = time.perf_counter()
    run()
    elapsed = time.perf_counter() - start
    print()
    print(f"elapsed: {elapsed:.2f}s")
