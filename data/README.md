# The CGSS microdata used by this project is NOT stored in this repository.

To reproduce the analysis you need to obtain the cleaned CGSS files yourself:

1. Download **CGSS 2017** and **CGSS 2023** from the official distributor
   (https://cgss.ruc.edu.cn/) and follow its terms of use.
2. Run the cleaning script to derive the analysis variables used here
   (`trust_bin`, `trust_pomp`, `cohort`, `internet`, `fairness`, `econ_subj`,
   `wt`, `s41`, `s42`, ...).
3. Place the resulting `CGSS2017.dta` and `CGSS2023.dta` in a folder and point
   the environment variable `CGSS_DATA_DIR` at it.

Why not included: the CGSS licence permits academic use but does not allow
redistribution of microdata, and the files contain survey responses that must
not be republished. Sharing them here would breach that licence.
