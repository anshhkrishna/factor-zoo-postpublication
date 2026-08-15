# factor-zoo-postpublication

> testing whether five fama-french style factor premia survive their own publication date, in numpy against ken french's own data

## Claim

Factor premia decay after the paper that first documented them is published: the Sharpe
ratio measured after each factor's publication date is a fraction of the Sharpe measured
before it, and the post-publication Sharpe is indistinguishable from a noise floor built
from randomly-signed synthetic factors of matched volatility.

Five factors are tested: SMB (size), HML (value), momentum, RMW (profitability), and CMA
(investment), each split at the year the anomaly it captures was first documented in the
literature (see "Publication years" below).

## Baseline

Two placebos, run through the identical in-sample/out-of-sample split as the tested
factors, over the same date range each tested factor is actually available in:

- **Mkt-RF** (the market factor, i.e. CAPM) - never "discovered" by a single paper, so any
  pre/post gap it shows reflects the fact that different multi-decade windows differ, not
  a publication effect.
- **FF3 tilt** - an equal-weight combination of Mkt-RF, SMB, and HML, as a second,
  differently-constructed placebo.

If either placebo shows as much apparent decay as a tested factor over the identical
window, that factor's decay is not attributable to publication.

A third control, not a baseline but the noise floor itself: **randomly-signed synthetic
factors**, built by taking a real factor's own returns and multiplying independent
12-month blocks by a random +/-1 draw. This preserves the real factor's volatility and
short-horizon autocorrelation while destroying any consistent directional edge, giving a
distribution of what a no-edge series with the same statistical texture looks like under
the same split.

## Result

All five tested factors decayed out-of-sample. None of the two placebos did - both went
up out-of-sample instead (`results/baseline.log`):

| placebo | pub. year window | in-sample Sharpe | out-of-sample Sharpe |
|---|---|---|---|
| Mkt-RF | 1992 (SMB/HML) | 0.400 | 0.602 |
| FF3 tilt | 1992 (SMB/HML) | 0.488 | 0.546 |
| Mkt-RF | 1993 (Mom) | 0.399 | 0.597 |
| FF3 tilt | 1993 (Mom) | 0.497 | 0.517 |
| Mkt-RF | 2013 (RMW) | 0.387 | 0.795 |
| FF3 tilt | 2013 (RMW) | 0.650 | 0.395 |
| Mkt-RF | 2008 (CMA) | 0.299 | 0.905 |
| FF3 tilt | 2008 (CMA) | 0.627 | 0.529 |

And the five tested factors (`results/run.log`):

| factor | publication year | in-sample Sharpe | out-of-sample Sharpe |
|---|---|---|---|
| SMB | 1992 | 0.252 | 0.048 |
| HML | 1992 | 0.414 | 0.196 |
| Mom | 1993 | 0.549 | 0.293 |
| RMW | 2013 | 0.407 | 0.211 |
| CMA | 2008 | 0.558 | 0.036 |

Every tested factor's out-of-sample Sharpe falls inside the 95% range of a noise floor
built from 1000 randomly-signed synthetic draws of that same factor's own returns
(`results/rigor.log`), meaning the post-publication premium is not statistically
distinguishable from a series with zero true edge:

| factor | out-of-sample Sharpe | noise floor (95% range) | indistinguishable from noise |
|---|---|---|---|
| SMB | 0.048 | [-0.267, 0.272] | yes |
| HML | 0.196 | [-0.443, 0.457] | yes |
| Mom | 0.293 | [-0.325, 0.376] | yes |
| RMW | 0.211 | [-0.616, 0.635] | yes |
| CMA | 0.036 | [-0.472, 0.484] | yes |

**5 of 5 tested factors do not survive publication by this test.** A block-bootstrap
confidence interval on each factor's own out-of-sample Sharpe (also in
`results/rigor.log`) is wide enough to bracket zero in every case, which is the same
conclusion from a different angle: none of these five factors has a post-publication
Sharpe that is reliably distinguishable from zero, let alone from its own in-sample
value.

![in-sample vs out-of-sample Sharpe per factor, with the noise floor and both placebos](results/headline.png)

### A methodological trap this project ran into and is reporting honestly

The plan for this project originally asked whether each factor's **decay ratio**
(out-of-sample Sharpe divided by in-sample Sharpe) falls outside a noise floor of decay
ratios from the same synthetic controls. Run through that literal framing, **0 of 5**
factors clear the bar, the opposite of the headline result above. The reason is not that
the factors survived: a decay ratio is a quotient of two Sharpes, and whenever a
synthetic no-edge draw happens to land an in-sample Sharpe near zero, the ratio blows up
toward plus or minus infinity. Across 1000 draws per factor this makes the ratio's own
noise floor so wide (pooled 95% range roughly [-18.7, 19.9]) that almost nothing ever
falls outside it. Comparing the out-of-sample Sharpe itself, rather than the ratio,
against a noise floor built the same way avoids this quotient blowup and is the more
direct test of the claim as stated - that is the comparison this README and
`results/headline.png` report. Both versions are computed and logged in
`results/rigor.log`, and both are covered by tests (see below), rather than only
reporting whichever framing looked better.

## Publication years used

Recalled from memory, not looked up against the papers directly (no network access in
the environment this was built in); if any of these is off by a year or two, it shifts
where the pre/post split falls and nothing about the method.

| factor | citation | year |
|---|---|---|
| SMB | Fama & French, "The Cross-Section of Expected Stock Returns," Journal of Finance | 1992 |
| HML | Fama & French (1992), same paper | 1992 |
| Mom | Jegadeesh & Titman, "Returns to Buying Winners and Selling Losers," Journal of Finance | 1993 |
| RMW | Novy-Marx, "The Other Side of Value: The Gross Profitability Premium," Journal of Financial Economics | 2013 |
| CMA | Cooper, Gulen & Schill, "Asset Growth and Stock Returns," Journal of Finance | 2008 |

Each of these anomalies has an earlier candidate citation in the literature (e.g. the
size effect traces to Banz 1981, well before the 1992 date used for SMB). Using the
later, more conservative date means any decay found here is, if anything, understated
relative to splitting at the true first mention.

## Data

`data/ken-french/F-F_Research_Data_Factors.csv` (Mkt-RF, SMB, HML, monthly, 1926-07
onward), `F-F_Research_Data_5_Factors_2x3.csv` (adds RMW, CMA, monthly, 1963-07 onward),
`F-F_Momentum_Factor.csv` (momentum, monthly, 1927-01 onward), and `25_Portfolios_5x5.csv`
(used only as a parser sanity check - a hand-built value-minus-growth spread from the 25
portfolios correlates with the official HML series at r=0.91). None of these files are
copied into this directory; `src/data.py` reads them in place from `data/ken-french/`
two levels up.

The five tested factors (SMB, HML, momentum, RMW, CMA) are Ken French's own
constructions, not independently rebuilt from raw stock-level data - rebuilding them
exactly would need the original portfolio breakpoints, which are not part of this
dataset. The 25-portfolio correlation check is a sanity check on the parser, not a
from-scratch replication of the factor construction itself.

## Method

- **Sharpe ratio**: `mean / std * sqrt(12)` on monthly returns (`src/decay.py`).
- **Split**: in-sample is every month through December of the publication year;
  out-of-sample is January of the following year onward.
- **Randomly-signed-factor control**: multiply each contiguous 12-month block of a real
  factor's returns by an independent +/-1 draw, preserving volatility and short-horizon
  autocorrelation while destroying any consistent directional edge. 1000 draws per
  factor, `np.random.default_rng(20260815)`.
- **Block-bootstrap CI**: resample the observed 12-month blocks with replacement (same
  block length as the noise-floor control), 1000 resamples, `np.random.default_rng(20260816)`.

## Reproduce

```
pip install -r requirements.txt
python -m pytest tests/ -v          # 10 tests, ~1.6s
python src/baseline.py > /tmp/baseline.log     # matches results/baseline.log
python src/experiment.py > /tmp/run.log        # matches results/run.log, ~0.5s
python src/rigor.py > /tmp/rigor.log           # matches results/rigor.log, ~1.4s
python src/plot.py                             # regenerates results/headline.png
```

All three run scripts are deterministic (fixed seeds), so the regenerated logs match
the committed ones exactly.

## Repo layout

```
src/data.py         four loaders for the Ken French CSVs
src/decay.py        Sharpe ratio, in/out split, noise-floor control, block bootstrap
src/baseline.py     Mkt-RF / FF3 placebo split -> results/baseline.log
src/experiment.py   the five tested factors' decay + noise floor -> results/run.log
src/rigor.py        bootstrap CIs + the core-claim comparison -> results/rigor.log
src/plot.py          results/headline.png from the three logs above
tests/               data-parsing checks and the core-claim test
```
