# Data files — de-identified derived datasets

This folder contains the analysis variables built from the CGSS 2017 and 2023
surveys. **All direct identifiers have been removed** (respondent `id`,
province code `s41`, city code `s42`, and `s43`), so the data cannot be traced
back to any individual.

| File | Rows | Description |
|---|---|---|
| `cgss2017_analysis.csv` | 12,582 | CGSS 2017, cleaned analysis variables |
| `cgss2023_analysis.csv` | 11,326 | CGSS 2023, cleaned analysis variables |
| `cgss_pooled_2017_2023.csv` | 23,908 | Both waves appended, with `wt_n` / `incq` / `s42c` derived |

**Key columns**

| Column | Meaning |
|---|---|
| `trust_bin` | Binary judicial trust (1 = trusts); harmonised across waves |
| `trust_pomp` | 0–1 standardised trust score |
| `trust_c5`, `trust_c7` | Alternative-cut-point variants of `trust_bin` |
| `cohort` | Birth cohort, 1 = born ≤1949 … 6 = born 1990+ |
| `internet` | Internet-use frequency, 1 = never … 5 = very frequently |
| `fairness` | Perceived social fairness |
| `econ_subj` | Subjective household economic status |
| `wt` | Original CGSS survey weight |
| `wt_n` | Weight normalised *within* year (pooled file only) |
| `incq` | Within-year income quintile, 0 = income missing |
| `s42c` | Prefecture-city code, used for clustered standard errors |
| `province` | Province name (added in place of the numeric code) |

## Why the raw CGSS microdata is not here

The CGSS licence permits academic, non-commercial **use** but does not permit
redistribution of the microdata. Respondents' answers must not be republished
in a form that could be re-linked to them. Shipping these derived,
identifier-free variables lets anyone reproduce the analysis while respecting
that licence.

To rebuild these files from scratch:

1. Obtain CGSS 2017 and 2023 from <https://cgss.ruc.edu.cn/>.
2. Run the cleaning step to construct the analysis variables.
3. Run `python src/prepare_public_data.py` (adapt the source paths), which
   drops the identifier columns and writes the files above.
