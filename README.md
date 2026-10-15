# Did Digital Media Erode Trust in China's Courts?

**A two-wave analysis of public judicial trust using CGSS 2017 and 2023**

---

## The problem

Over the past decade China has built one of the world's largest court
digitalisation programmes — judgments published online, e-litigation rules
implemented, "smart courts" rolled out nationwide. At the same time,
algorithm-driven platforms have become the main channel through which the
public encounters judicial news.

This raises a question that policy debate frequently assumes but rarely
tests with national data:

> **Does the spread of digital media erode public trust in the judiciary?**

The worry is plausible in both directions: digitalisation is promoted as a
lever for judicial transparency and legitimacy, yet viral coverage of
individual cases may also corrode institutional trust. This project puts
both narratives in front of the same representative data.

## Repository layout

```
data-science-project/
├── README.md
├── requirements.txt
├── CGSS_judicial_trust_analysis.ipynb   # main analysis notebook (pre-executed)
├── data/                                # de-identified derived datasets (CSV)
│   ├── cgss2017_analysis.csv
│   ├── cgss2023_analysis.csv
│   ├── cgss_pooled_2017_2023.csv
│   └── README.md
├── src/
│   ├── analysis.py                # headline statistics (command-line script)
│   ├── make_figures.py            # four English-language figures
│   ├── prepare_public_data.py     # builds the de-identified CSVs
│   └── build_notebook.py          # regenerates the notebook programmatically
└── figures/                       # output visualisations
```

## Data source and usage permissions

| Item | Detail |
|---|---|
| Primary data | **China General Social Survey (CGSS)**, waves **2017** and **2023** |
| Access | Publicly released microdata from the official CGSS distributor (**cgss.ruc.edu.cn**), which permits academic non-commercial use |
| Analysis samples | 2017: *n* = 3,953 · 2023: *n* = 5,583 (respondents with a valid judicial-trust answer) |
| Secondary data | Tsinghua *Digital Government Development Index* (2022), published provincial scores |
| Policy corpus | Keyword counts from the public websites of the Supreme People's Court, the Ministry of Justice and the Cyberspace Administration of China (2014–2024) |
| What is shipped | **De-identified, derived datasets only** — respondent IDs and geographic identifiers removed |
| What is *not* shipped | Raw CGSS microdata, personal identifiers, and restricted datasets |

The raw CGSS microdata is **not** redistributed here: its licence permits
academic use but not republication. The `data/` folder contains the
**derived analysis variables** (trust measures, cohort, education, internet
use, weights, …) with all direct identifiers stripped, so the analysis is
fully reproducible without republishing the survey itself. See
[`data/README.md`](data/README.md).

## Methods and tools

- **Python** — pandas, NumPy, statsmodels, matplotlib
- **Estimator** — linear probability model (LPM), so coefficients read
  directly as percentage-point differences
- **Weights** — CGSS sampling weights, normalised *within* each wave so the
  two waves contribute equally to pooled estimates
- **Inference** — standard errors clustered at the **prefecture-city** level
  (equivalent to Stata's `reg y x [pw=wt_n], vce(cluster s42c)`)
- **Measurement harmonisation** — the trust question differs across waves
  (0–10 scale about *courts* in 2017 vs. a 4-point scale about *judges* in
  2023). Rather than compare raw means, three outcomes are reported: a binary
  trust indicator, a 0–1 POMP score, and alternative cut-points.

## Key findings

1. **Judicial trust rose sharply.** The weighted trust rate climbed from
   **61.9% (2017) to 83.1% (2023)**, i.e. **+21.2 percentage points**; the
   harmonised POMP score rose **+4.8 pp**. The direction is consistent across
   every measurement choice.
2. **The rise was broadly shared, not polarised.** The urban–rural gap
   (*p* = 0.54) and the education gradient (*p* = 0.97) were unchanged, so the
   increase was **inclusive**.
3. **The 1980s cohort moved most.** Trust among those born in the 1980s rose
   **+29.4 pp** (55.6% → 85.0%), the largest gain of any cohort, as
   generational gaps converged.
4. **Geography confirms it.** In every one of the 16 matched provinces the
   2023 trust rate sits **above** the 2017 level.
5. **Internet use is modestly negative — and fading.** Adjusting for
   demographics and socio-economic status, trust probability falls by about
   **0.8 pp per step** up the internet-use scale, but the association is
   **not significant in the full specification** (*p* = 0.11). In the
   wave-specific models it is negative and significant in 2017 but not in
   2023 — consistent with a **narrowing** rather than widening digital divide.
6. **Trust tracks subjective experience, not technology exposure.**
   Perceived **fairness** is the strongest predictor of trust (+7.0 pp per
   step), while the provincial Digital Government Index shows **no significant
   association** with judicial trust (*r* = −0.13, *n* = 16).

> **Bottom line:** whether a court is digitalised does not determine public
> trust — *how* it is digitalised does.

### One limitation

The two CGSS waves measured judicial trust with **different scales and
different referents** (courts vs. judges). The harmonisation strategy makes
the *direction* of the change robust, but it cannot perfectly recover the
true magnitude — the "+21 pp" figure should be read as one defensible
estimate among several, not an exact true effect. Province coverage in 2023
is also limited to 16 provinces, which caps the power of the provincial
analysis.

## Figures

| Figure | What it shows |
|---|---|
| `figures/fig1_cohort_trust_en.png` | Trust rate by birth cohort, 2017 vs 2023 |
| `figures/fig2_province_shift_en.png` | Provincial trust: every matched province rose above the 45° line |
| `figures/fig3_policy_trend_en.png` | Digital-justice policy discourse, 2014–2024 |
| `figures/fig4_dgi_scatter_en.png` | Digital Government Index vs. judicial trust (*n* = 16) |
| `figures/fig_trust_levels.png` | Headline change, 61.9% → 83.1% (from the notebook) |
| `figures/fig_cohort.png` | Cohort breakdown (from the notebook) |
| `figures/fig_internet.png` | Adjusted trust by internet-use frequency (from the notebook) |

## How to run

```bash
# 1. install dependencies
pip install -r requirements.txt

# 2a. run the notebook (recommended) — it is shipped already executed
jupyter notebook CGSS_judicial_trust_analysis.ipynb

# 2b. or run the command-line analysis
python src/analysis.py          # headline statistics
python src/make_figures.py      # regenerate the four figures
```

To reproduce the study **from the raw survey**, obtain CGSS 2017 and 2023
from the official distributor, run the cleaning step to build the analysis
variables, then use `src/prepare_public_data.py` as the reference for how the
shipped CSVs are formed (it also strips identifiers).

## Author

**WANG Weicheng** — MSc in Data Science, University of Macau.
Research interests: computational social science, judicial politics, and
digital governance.

*Project status: **ongoing** — a working paper being prepared for a
public-governance data-analysis competition and a computational-sociology
conference.*
