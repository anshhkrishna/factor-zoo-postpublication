# factor-zoo-postpublication

> testing whether five fama-french style factor premia survive their own publication date

## Claim

Factor premia decay after the paper that first documented them is published: the
Sharpe ratio measured after each factor's publication date is a fraction of the Sharpe
measured before it, and for at least some factors the post-publication Sharpe is
indistinguishable from a noise floor built from randomly-signed synthetic factors of
matched volatility.

## Baseline

The market factor (Mkt-RF, i.e. CAPM) and the combined Fama-French 3-factor tilt,
evaluated over the identical pre/post split each tested factor uses, as a placebo:
the market was never "discovered" by a single paper, so any pre/post gap it shows is
attributable to macroeconomic regime rather than a publication effect. A
randomly-signed-factor control (real factor volatility, randomized sign) establishes
the noise floor a decay ratio needs to clear before it means anything.

## Status

Planning only so far. Implementation, results, and the reproduce instructions land as
each step of the project completes.
