# Data

The four Ken French data library files this project reads, committed here so the repo
clones and reproduces with no network access and no account.

| file | contents |
|---|---|
| `ken-french/F-F_Research_Data_Factors.csv` | 3-factor monthly (Mkt-RF, SMB, HML, RF), 1926-07 onward |
| `ken-french/F-F_Research_Data_5_Factors_2x3.csv` | 5-factor monthly (adds RMW, CMA), 1963-07 onward |
| `ken-french/F-F_Momentum_Factor.csv` | momentum monthly, 1927-01 onward |
| `ken-french/25_Portfolios_5x5.csv` | 25 portfolios formed on size and book-to-market, used only as a parser sanity check |

Downloaded 2026-08-14 from the Ken French data library at Dartmouth, unzipped, and
otherwise unmodified. `MANIFEST.tsv` records each file's size, SHA-256, source URL, and
retrieval date, so anything here can be checked against a fresh download.

## Parse quirks

These CSVs are not plain tables. Each file opens with a block of prose, then a header row
that begins with a comma, then monthly rows keyed by a `YYYYMM` date, then a blank line
that ends the monthly section. Several files continue past that blank line with annual
tables or a second set of portfolios, so a parser has to stop at the first blank line
rather than reading to end of file.

Values are in percent, not decimals. Missing observations are coded `-99.99` or `-999`
rather than left empty. `src/data.py` converts both codes to NaN and leaves the units
alone.

## License

The data is redistributed here for reproducibility. It remains the work of Eugene Fama
and Kenneth French, and the library's own terms at the source page govern its use.
