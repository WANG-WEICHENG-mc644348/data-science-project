"""Regenerate the cleaned CSVs for the portfolio repo (de-identified).

Drops respondent-identifier columns (id, s41, s42, s43) from the derived
analysis datasets, keeping only the variables needed to reproduce the study.
Also derives province/region names in place of raw numeric province codes.
"""
import os
import pandas as pd

SRC = r"C:\Users\26781\Desktop\CGSS\李思危转为python格式的旧版本代码与数据"
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DST, exist_ok=True)

PROV = {1: "Shanghai", 2: "Yunnan", 3: "Inner Mongolia", 4: "Beijing",
        5: "Jilin", 6: "Sichuan", 7: "Tianjin", 8: "Ningxia", 9: "Anhui",
        10: "Shandong", 11: "Shanxi", 12: "Guangdong", 13: "Guangxi",
        14: "Xinjiang", 15: "Jiangsu", 16: "Jiangxi", 17: "Hebei",
        18: "Henan", 19: "Zhejiang", 20: "Hainan", 21: "Hubei",
        22: "Hunan", 23: "Gansu", 24: "Fujian", 25: "Tibet", 26: "Guizhou",
        27: "Liaoning", 28: "Chongqing", 29: "Shaanxi", 30: "Qinghai",
        31: "Heilongjiang"}

DROP_ID = ["id", "s41", "s42", "s43"]


def clean(path, out, add_geo=False):
    d = pd.read_csv(path, encoding="utf-8-sig")
    if add_geo and "s41" in d.columns:
        d["province"] = d["s41"].map(PROV)
    keep = [c for c in d.columns if c not in DROP_ID]
    d = d[keep]
    d = d.drop(columns=[c for c in d.columns if c.startswith("Unnamed")])
    d.to_csv(os.path.join(DST, out), index=False, encoding="utf-8-sig")
    print(f"{out:<42} rows={len(d):>6}  cols={len(d)}")
    return list(d.columns)


for f, o, geo in [
    ("CGSS2017_cleaned_reference.csv", "cgss2017_analysis.csv", True),
    ("CGSS2023_cleaned_python.csv", "cgss2023_analysis.csv", True),
    ("CGSS2017_2023_pooled_python.csv", "cgss_pooled_2017_2023.csv", True),
]:
    cols = clean(os.path.join(SRC, f), o, add_geo=geo)
    if f.startswith("CGSS2017_2023"):
        print("  pooled columns:", ", ".join(cols))
