"""
analysis.py — Reproduce the core statistics of the CGSS judicial-trust study.

Research question
-----------------
Did the rise of digital media erode public trust in the judiciary in China?

Design
------
Two waves of the China General Social Survey (CGSS 2017, 2023) are pooled.
The judicial-trust question changed format between waves (an 11-point scale
in 2017 vs. a 4-point scale in 2023), so the analysis is deliberately
"measurement transparent": three harmonised outcome definitions are reported
instead of a single one.

Estimator
---------
Linear probability model (LPM), survey weights normalised within year, and
standard errors clustered at the prefecture-city level. This is numerically
equivalent to Stata's `reg y x [pw=wt_n], vce(cluster s42c)`.

Outputs (stdout)
----------------
  1. Weighted trust rate / POMP score by wave
  2. Three nested LPM specifications (M1 base / M2 + socio-economic / M3 + attitudes)
  3. Cohort x wave interaction test (who moved the most?)

Usage
-----
  export CGSS_DATA_DIR=/path/to/clean/cgss/files
  python src/analysis.py
"""
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA_DIR = os.environ.get("CGSS_DATA_DIR", r"C:\Users\26781\Desktop\CGSS")


def wmean(x, w):
    m = pd.notna(x) & pd.notna(w)
    return float(np.average(np.asarray(x)[m], weights=np.asarray(w)[m]))


def load_pooled():
    """Pool the two cleaned waves and build the analysis variables."""
    d17 = pd.read_stata(os.path.join(DATA_DIR, "CGSS2017.dta"), convert_categoricals=False)
    d23 = pd.read_stata(os.path.join(DATA_DIR, "CGSS2023.dta"), convert_categoricals=False)
    d = pd.concat([d17, d23], ignore_index=True)

    # --- weights normalised within year (so the two waves are equally weighted) ---
    d["n_year"] = d.groupby("year")["year"].transform("size")
    d["w_year"] = d.groupby("year")["wt"].transform("sum")
    d["wt_n"] = d["wt"] * d["n_year"] / d["w_year"]

    # --- within-year income quintile (household income inflates across waves) ---
    d["incq"] = np.nan
    for y in d["year"].unique():
        m = d["year"] == y
        d.loc[m, "incq"] = pd.qcut(d.loc[m, "lninc"], 5,
                                   labels=False, duplicates="drop") + 1
    d["incq"] = d["incq"].fillna(0)          # 0 = income missing

    # --- year dummy + city cluster id ---
    d["y2023"] = (d["year"] == 2023).astype(float)
    d["city"] = d["s42"]
    for c in ["cohort", "hukou", "region", "empstat", "incq"]:
        d[c] = pd.Categorical(d[c])
    return d


def describe(d):
    print("=" * 68)
    print("1. WEIGHTED TRUST LEVELS BY WAVE")
    print("=" * 68)
    m = d["trust_bin"].notna()
    for y in [2017, 2023]:
        s = d[m & (d.year == y)]
        print(f"  {y}: n = {len(s):>5}  |  trust rate = "
              f"{wmean(s.trust_bin, s.wt_n):.4f}  |  POMP = "
              f"{wmean(s.trust_pomp, s.wt_n):.4f}")
    r17 = wmean(d[m & (d.year == 2017)].trust_bin, d[m & (d.year == 2017)].wt_n)
    r23 = wmean(d[m & (d.year == 2023)].trust_bin, d[m & (d.year == 2023)].wt_n)
    p17 = wmean(d[m & (d.year == 2017)].trust_pomp, d[m & (d.year == 2017)].wt_n)
    p23 = wmean(d[m & (d.year == 2023)].trust_pomp, d[m & (d.year == 2023)].wt_n)
    print(f"\n  Change 2017->2023: binary {(r23-r17)*100:+.2f} pp  |  "
          f"POMP {(p23-p17)*100:+.2f} pp")


def models(d):
    print()
    print("=" * 68)
    print("2. NESTED LINEAR PROBABILITY MODELS (DV = trust_bin)")
    print("=" * 68)
    base = ("y2023 + C(cohort) + female + edu_years + C(hukou) + party "
            "+ C(region)")
    econ = " + econ_subj + C(incq) + si_any + C(empstat) + internet"
    attit = " + fairness + social_trust + know_lawyer + know_police"

    need = ["trust_bin", "y2023", "cohort", "female", "edu_years", "hukou",
            "party", "region", "econ_subj", "incq", "si_any", "empstat",
            "internet", "city"]
    sub = d.dropna(subset=need).copy()

    specs = {"M1 base": base, "M2 +socio-econ": base + econ,
             "M3 +attitudes": base + econ + attit}
    focus = ["y2023", "fairness", "econ_subj", "internet"]
    print(f"{'variable':<14}" + "".join(f"{k:>17}" for k in specs))
    fitted = {}
    for k, f in specs.items():
        s = sub.dropna(subset=[c for c in ("fairness", "social_trust",
                                           "know_lawyer", "know_police")
                               if c in f]).copy()
        mod = smf.wls("trust_bin ~ " + f, data=s, weights=s["wt_n"]).fit(
            cov_type="cluster", cov_kwds={"groups": s["city"]})
        fitted[k] = mod
    for v in focus:
        row = f"{v:<14}"
        for k in specs:
            mod = fitted[k]
            if v in mod.params:
                star = "***" if mod.pvalues[v] < .01 else \
                       "**" if mod.pvalues[v] < .05 else \
                       "*" if mod.pvalues[v] < .10 else ""
                row += f"{mod.params[v]:>+15.4f}{star:>2}"
            else:
                row += f"{'--':>17}"
        print(row)
    print("\n  N: " + "  ".join(f"{k}={int(m.nobs)}" for k, m in fitted.items()))
    print("  Stars: * p<.10  ** p<.05  *** p<.01   (SE clustered by prefecture city)")


def heterogeneity(d):
    print()
    print("=" * 68)
    print("3. WHO MOVED THE MOST?  (wave x group interactions)")
    print("=" * 68)
    need = ["trust_bin", "y2023", "cohort", "female", "edu_years", "hukou",
            "party", "region", "econ_subj", "incq", "si_any", "empstat",
            "internet", "city"]
    sub = d.dropna(subset=need).copy()

    f = ("trust_bin ~ y2023 * C(cohort) + female + edu_years + C(hukou) "
         "+ party + C(region) + econ_subj + C(incq) + si_any + C(empstat) "
         "+ internet")
    mod = smf.wls(f, data=sub, weights=sub["wt_n"]).fit(
        cov_type="cluster", cov_kwds={"groups": sub["city"]})
    terms = [t for t in mod.params.index if "y2023:C(cohort)" in t]
    print("  wave x cohort joint test:")
    print(f"    Wald chi2 = {mod.f_test(' = 0, '.join(terms)+' = 0').fvalue:8.2f}"
          f"   p = {mod.f_test(' = 0, '.join(terms)+' = 0').pvalue:.4f}")
    print(f"  {'cohort':<16}{'2017 rate':>11}{'2023 rate':>11}{'change (pp)':>13}")
    lab = {1: "<=1949", 2: "1950s", 3: "1960s", 4: "1970s", 5: "1980s", 6: "1990s+"}
    for c in sorted(sub["cohort"].cat.categories):
        for y in (2017, 2023):
            pass
        s = sub[sub["cohort"] == c]
        a = wmean(s[s.year == 2017].trust_bin, s[s.year == 2017].wt_n)
        b = wmean(s[s.year == 2023].trust_bin, s[s.year == 2023].wt_n)
        print(f"  {lab.get(c, c):<16}{a*100:>10.1f}%{b*100:>10.1f}%{(b-a)*100:>12.1f}")

    # hukou and education interactions
    f2 = ("trust_bin ~ y2023 * C(hukou) + C(cohort) + female + edu_years "
          "+ party + C(region) + econ_subj + C(incq) + si_any + C(empstat) "
          "+ internet")
    m2 = smf.wls(f2, data=sub, weights=sub["wt_n"]).fit(
        cov_type="cluster", cov_kwds={"groups": sub["city"]})
    t2 = [t for t in m2.params.index if "y2023:C(hukou)" in t]
    print(f"\n  wave x hukou test:  p = "
          f"{m2.f_test(' = 0, '.join(t2)+' = 0').pvalue:.3f}   (n.s. = stable urban/rural gap)")

    f3 = ("trust_bin ~ y2023 * edu_years + C(cohort) + female + C(hukou) "
          "+ party + C(region) + econ_subj + C(incq) + si_any + C(empstat) "
          "+ internet")
    m3 = smf.wls(f3, data=sub, weights=sub["wt_n"]).fit(
        cov_type="cluster", cov_kwds={"groups": sub["city"]})
    print(f"  wave x education test: p = "
          f"{m3.pvalues.get('y2023:edu_years', float('nan')):.3f}   "
          f"(n.s. = unchanged education gradient)")


if __name__ == "__main__":
    d = load_pooled()
    describe(d)
    models(d)
    heterogeneity(d)
    print("\nDone.")
