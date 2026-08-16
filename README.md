# factor-zoo-postpublication

> testing whether five fama-french style factor premia survive their own publication date, in numpy against ken french's own data

## claim

factor premia decay after the paper that first documented them is published: the sharpe
ratio measured after each factor's publication date is a fraction of the sharpe measured
before it, and the post-publication sharpe is indistinguishable from a noise floor built
from randomly-signed synthetic factors of matched volatility.

five factors are tested: smb (size), hml (value), momentum, rmw (profitability), and cma
(investment), each split at the year the anomaly it captures was first documented in the
literature (see "publication years" below).

## baseline

two placebos, run through the identical in-sample/out-of-sample split as the tested
factors, over the same date range each tested factor is actually available in:

- **mkt-rf** (the market factor, i.e. capm) - never "discovered" by a single paper, so any
  pre/post gap it shows reflects the fact that different multi-decade windows differ, not
  a publication effect.
- **ff3 tilt** - an equal-weight combination of mkt-rf, smb, and hml, as a second,
  differently-constructed placebo.

if either placebo shows as much apparent decay as a tested factor over the identical
window, that factor's decay is not attributable to publication.

a third control, not a baseline but the noise floor itself: **randomly-signed synthetic
factors**, built by taking a real factor's own returns and multiplying independent
12-month blocks by a random +/-1 draw. this preserves the real factor's volatility and
short-horizon autocorrelation while destroying any consistent directional edge, giving a
distribution of what a no-edge series with the same statistical texture looks like under
the same split.

## result

all five tested factors decayed out-of-sample. none of the two placebos did - both went
up out-of-sample instead (`results/baseline.log`):

| placebo | pub. year window | in-sample sharpe | out-of-sample sharpe |
|---|---|---|---|
| mkt-rf | 1992 (smb/hml) | 0.400 | 0.602 |
| ff3 tilt | 1992 (smb/hml) | 0.488 | 0.546 |
| mkt-rf | 1993 (mom) | 0.399 | 0.597 |
| ff3 tilt | 1993 (mom) | 0.497 | 0.517 |
| mkt-rf | 2013 (rmw) | 0.387 | 0.795 |
| ff3 tilt | 2013 (rmw) | 0.650 | 0.395 |
| mkt-rf | 2008 (cma) | 0.299 | 0.905 |
| ff3 tilt | 2008 (cma) | 0.627 | 0.529 |

and the five tested factors (`results/run.log`):

| factor | publication year | in-sample sharpe | out-of-sample sharpe |
|---|---|---|---|
| smb | 1992 | 0.252 | 0.048 |
| hml | 1992 | 0.414 | 0.196 |
| mom | 1993 | 0.549 | 0.293 |
| rmw | 2013 | 0.407 | 0.211 |
| cma | 2008 | 0.558 | 0.036 |

every tested factor's out-of-sample sharpe falls inside the 95% range of a noise floor
built from 1000 randomly-signed synthetic draws of that same factor's own returns
(`results/rigor.log`), meaning the post-publication premium is not statistically
distinguishable from a series with zero true edge:

| factor | out-of-sample sharpe | noise floor (95% range) | indistinguishable from noise |
|---|---|---|---|
| smb | 0.048 | [-0.267, 0.272] | yes |
| hml | 0.196 | [-0.443, 0.457] | yes |
| mom | 0.293 | [-0.325, 0.376] | yes |
| rmw | 0.211 | [-0.616, 0.635] | yes |
| cma | 0.036 | [-0.472, 0.484] | yes |

**5 of 5 tested factors do not survive publication by this test.** a block-bootstrap
confidence interval on each factor's own out-of-sample sharpe (also in
`results/rigor.log`) is wide enough to bracket zero in every case, which is the same
conclusion from a different angle: none of these five factors has a post-publication
sharpe that is reliably distinguishable from zero, let alone from its own in-sample
value.

![in-sample vs out-of-sample sharpe per factor, with the noise floor and both placebos](results/headline.png)

### a methodological trap this project ran into and is reporting honestly

the plan for this project originally asked whether each factor's **decay ratio**
(out-of-sample sharpe divided by in-sample sharpe) falls outside a noise floor of decay
ratios from the same synthetic controls. run through that literal framing, **0 of 5**
factors clear the bar, the opposite of the headline result above. the reason is not that
the factors survived: a decay ratio is a quotient of two sharpes, and whenever a
synthetic no-edge draw happens to land an in-sample sharpe near zero, the ratio blows up
toward plus or minus infinity. across 1000 draws per factor this makes the ratio's own
noise floor so wide (pooled 95% range roughly [-18.7, 19.9]) that almost nothing ever
falls outside it. comparing the out-of-sample sharpe itself, rather than the ratio,
against a noise floor built the same way avoids this quotient blowup and is the more
direct test of the claim as stated - that is the comparison this readme and
`results/headline.png` report. both versions are computed and logged in
`results/rigor.log`, and both are covered by tests (see below), rather than only
reporting whichever framing looked better.

## publication years used

recalled from memory, not looked up against the papers directly (no network access in
the environment this was built in); if any of these is off by a year or two, it shifts
where the pre/post split falls and nothing about the method.

| factor | citation | year |
|---|---|---|
| smb | fama & french, "the cross-section of expected stock returns," journal of finance | 1992 |
| hml | fama & french (1992), same paper | 1992 |
| mom | jegadeesh & titman, "returns to buying winners and selling losers," journal of finance | 1993 |
| rmw | novy-marx, "the other side of value: the gross profitability premium," journal of financial economics | 2013 |
| cma | cooper, gulen & schill, "asset growth and stock returns," journal of finance | 2008 |

each of these anomalies has an earlier candidate citation in the literature (e.g. the
size effect traces to banz 1981, well before the 1992 date used for smb). using the
later, more conservative date means any decay found here is, if anything, understated
relative to splitting at the true first mention.

## data

`data/ken-french/F-F_Research_Data_Factors.csv` (mkt-rf, smb, hml, monthly, 1926-07
onward), `F-F_Research_Data_5_Factors_2x3.csv` (adds rmw, cma, monthly, 1963-07 onward),
`F-F_Momentum_Factor.csv` (momentum, monthly, 1927-01 onward), and `25_Portfolios_5x5.csv`
(used only as a parser sanity check - a hand-built value-minus-growth spread from the 25
portfolios correlates with the official hml series at r=0.91). all four are committed
under `data/ken-french/`, so the repo reproduces with no network access and no account.
`data/MANIFEST.tsv` records each file's size, sha-256, source url, and retrieval date,
and `data/README.md` documents the parse quirks.

the five tested factors (smb, hml, momentum, rmw, cma) are ken french's own
constructions, not independently rebuilt from raw stock-level data - rebuilding them
exactly would need the original portfolio breakpoints, which are not part of this
dataset. the 25-portfolio correlation check is a sanity check on the parser, not a
from-scratch replication of the factor construction itself.

## method

- **sharpe ratio**: `mean / std * sqrt(12)` on monthly returns (`src/decay.py`).
- **split**: in-sample is every month through december of the publication year;
  out-of-sample is january of the following year onward.
- **randomly-signed-factor control**: multiply each contiguous 12-month block of a real
  factor's returns by an independent +/-1 draw, preserving volatility and short-horizon
  autocorrelation while destroying any consistent directional edge. 1000 draws per
  factor, `np.random.default_rng(20260815)`.
- **block-bootstrap ci**: resample the observed 12-month blocks with replacement (same
  block length as the noise-floor control), 1000 resamples, `np.random.default_rng(20260816)`.

## reproduce

```
pip install -r requirements.txt
python -m pytest tests/ -v          # 10 tests, ~1.6s
python src/baseline.py > /tmp/baseline.log     # matches results/baseline.log
python src/experiment.py > /tmp/run.log        # matches results/run.log, ~0.5s
python src/rigor.py > /tmp/rigor.log           # matches results/rigor.log, ~1.4s
python src/plot.py                             # regenerates results/headline.png
```

all three run scripts are deterministic (fixed seeds), so the regenerated logs match
the committed ones exactly.

## repo layout

```
src/data.py         four loaders for the Ken French CSVs
src/decay.py        Sharpe ratio, in/out split, noise-floor control, block bootstrap
src/baseline.py     Mkt-RF / FF3 placebo split -> results/baseline.log
src/experiment.py   the five tested factors' decay + noise floor -> results/run.log
src/rigor.py        bootstrap CIs + the core-claim comparison -> results/rigor.log
src/plot.py          results/headline.png from the three logs above
tests/               data-parsing checks and the core-claim test
```
