"""
make_figures.py — Generate English-language visualizations for the
Data Science Portfolio (CGSS 2017/2023 judicial trust study).

Outputs (to ../figures/):
  fig1_cohort_trust_en.png      - trust rate by birth cohort, 2017 vs 2023
  fig2_province_shift_en.png    - provincial trust rate: 2017 vs 2023 scatter
  fig3_policy_trend_en.png      - smart-court policy discourse, 2014-2024
  fig4_dgi_scatter_en.png       - provincial trust vs digital gov index (n=16)

Run:  python src/make_figures.py
Data: expects CGSS2017.dta / CGSS2023.dta in the directory given by DATA_DIR.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})

DATA_DIR = os.environ.get("CGSS_DATA_DIR", r"C:\Users\26781\Desktop\CGSS")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(OUT, exist_ok=True)

C_2017, C_2023 = "#4C72B0", "#C44E52"


def load_pooled():
    d17 = pd.read_stata(os.path.join(DATA_DIR, "CGSS2017.dta"), convert_categoricals=False)
    d23 = pd.read_stata(os.path.join(DATA_DIR, "CGSS2023.dta"), convert_categoricals=False)
    d = pd.concat([d17, d23], ignore_index=True)
    d["ny"] = d.groupby("year")["year"].transform("size")
    d["wsum"] = d.groupby("year")["wt"].transform("sum")
    d["wt_n"] = d["wt"] * d["ny"] / d["wsum"]      # weights normalised within year
    return d


def wmean(x, w):
    m = pd.notna(x) & pd.notna(w)
    return np.average(np.asarray(x)[m], weights=np.asarray(w)[m]) if m.any() else np.nan


# ---------------------------------------------------------------- fig 1
def fig1_cohort(d):
    lab = {1: "Born <=1949", 2: "1950s", 3: "1960s",
           4: "1970s", 5: "1980s", 6: "1990s+"}
    s = d[d["trust_bin"].notna()]
    g = (s.groupby(["cohort", "year"])
           .apply(lambda x: wmean(x["trust_bin"], x["wt_n"]))
           .unstack("year"))
    x = np.arange(len(g))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.bar(x - w/2, g[2017]*100, w, label="2017", color=C_2017)
    ax.bar(x + w/2, g[2023]*100, w, label="2023", color=C_2023)
    for i, (a, b) in enumerate(zip(g[2017]*100, g[2023]*100)):
        ax.text(i - w/2, a + 0.8, f"{a:.0f}", ha="center", fontsize=8.5)
        ax.text(i + w/2, b + 0.8, f"{b:.0f}", ha="center", fontsize=8.5)
    ax.set_xticks(x)
    ax.set_xticklabels([lab[c] for c in g.index])
    ax.set_ylabel("Judicial trust rate (%)")
    ax.set_xlabel("Birth cohort")
    ax.set_title("Judicial trust rose most sharply for the 1980s cohort")
    ax.legend(frameon=False, ncol=2, loc="upper center",
              bbox_to_anchor=(0.5, 1.0), fontsize=10)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    fig.tight_layout()
    p = os.path.join(OUT, "fig1_cohort_trust_en.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# ---------------------------------------------------------------- fig 2
def fig2_province(d):
    s = d[d["trust_bin"].notna()].copy()
    g = s.groupby(["s41", "year"]).apply(
        lambda x: wmean(x["trust_bin"], x["wt_n"])).unstack("year")
    g = g.dropna()
    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    ax.scatter(g[2017]*100, g[2023]*100, s=42, color=C_2023,
               edgecolor="white", linewidth=0.8, zorder=3)
    lim = [40, 100]
    ax.plot(lim, lim, ls="--", lw=1, color="grey", zorder=1)
    ax.text(92, 88, "45\u00b0 line\n(no change)", fontsize=8.5, color="grey",
            ha="right")
    ax.set_xlim(*lim); ax.set_ylim(*lim)
    ax.set_xlabel("Trust rate 2017 (%)")
    ax.set_ylabel("Trust rate 2023 (%)")
    ax.set_title(f"Provincial trust, 2017 vs 2023 (n={len(g)})")
    ax.grid(alpha=0.25, zorder=0)
    fig.tight_layout()
    p = os.path.join(OUT, "fig2_province_shift_en.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# ---------------------------------------------------------------- fig 3
def fig3_policy():
    csv = os.path.join(DATA_DIR, "司法政策文本检索", "逐年计数表.csv")
    df = pd.read_csv(csv, encoding="utf-8-sig")
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    df[["年份", "智慧法院", "智慧司法", "人工智能司法"]] = df[
        ["年份", "智慧法院", "智慧司法", "人工智能司法"]].apply(
        pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["年份"])
    df = df[df["年份"] <= 2024].copy()
    years = df["年份"].astype(int)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    cols = {"智慧法院": "#4C72B0", "智慧司法": "#DD8452",
            "人工智能司法": "#55A868"}
    bottom = np.zeros(len(df))
    for zh, en in zip(cols, ["Smart courts", "Smart justice", "AI in justice"]):
        v = df[zh].astype(float).values
        ax.bar(years, v, bottom=bottom, label=en, color=cols[zh], width=0.7)
        bottom += v
    ax.plot(years, bottom, color="black", lw=1.2, marker="o", ms=3.5,
            label="Total", zorder=5)
    ax.annotate("2016: \"smart courts\"\nlaunched (5 hits)",
                xy=(2016, 5), xytext=(2015.6, 34), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=0.9, color="black"))
    ax.annotate("2023 peak (52)", xy=(2023, 52), xytext=(2020.4, 62),
                fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=0.9, color="black"))
    ax.set_xlabel("Year")
    ax.set_ylabel("Policy documents retrieved")
    ax.set_title("Digital-justice policy discourse, 2014\u20132024")
    ax.legend(frameon=False, ncol=2, fontsize=9, loc="upper left",
              bbox_to_anchor=(0.0, 1.0))
    ax.set_xticks(years)
    ax.set_ylim(0, 74)
    fig.tight_layout()
    p = os.path.join(OUT, "fig3_policy_trend_en.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p)


# ---------------------------------------------------------------- fig 4
def fig4_dgi():
    prov = pd.read_stata(os.path.join(DATA_DIR, "prov_scatter.dta"),
                         convert_categoricals=False)
    dgi = pd.read_stata(os.path.join(DATA_DIR, "dgi22.dta"),
                        convert_categoricals=False)
    keep = ["s41", "trust_bin2023"]
    m = prov[keep].merge(dgi[["s41", "total22"]], on="s41", how="inner")
    m = m.dropna()
    x, y = m["total22"], m["trust_bin2023"]*100
    r = np.corrcoef(x, y)[0, 1]
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.scatter(x, y, s=46, color="#55A868", edgecolor="white",
               linewidth=0.8, zorder=3)
    z = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, np.polyval(z, xs), color="#C44E52", lw=1.4, zorder=2)
    ax.set_xlabel("Digital Government Index 2022 (province score)")
    ax.set_ylabel("Judicial trust rate 2023 (%)")
    ax.set_title(f"Digital government \u00d7 judicial trust (n={len(m)}, r={r:+.2f})")
    ax.grid(alpha=0.25, zorder=0)
    fig.tight_layout()
    p = os.path.join(OUT, "fig4_dgi_scatter_en.png")
    fig.savefig(p); plt.close(fig)
    print("saved", p, "| r =", round(r, 3))


if __name__ == "__main__":
    d = load_pooled()
    fig1_cohort(d)
    fig2_province(d)
    fig3_policy()
    fig4_dgi()
    print("all figures written to", OUT)
