from typing import Dict, Any, Tuple, List
import pandas as pd
import re
from dataParsing import pbp

def parse_off_personnel(s: str) -> Tuple[int,int,int,str]:
    if not isinstance(s, str):
        print("personnel",s)
        return 0,0,0,"UNK"
    m = dict(re.findall(r"(\d+)\s*(RB|TE|WR)", s.upper()))
    rb: int = int(m.get("RB", 0))
    te: int = int(m.get("TE", 0))
    wr: int = int(m.get("WR", 0))
    grp: str = f"{rb}{te}" if (rb or te) else "UNK"  # e.g., "11","12","13","20","21","22"
    return rb, te, wr, grp

def parse_def_personnel(s: str) -> Tuple[int,int,int,str]:
    if not isinstance(s, str):
        return 0,0,0,"UNK"
    m = dict(re.findall(r"(\d+)\s*(DL|LB|DB)", s.upper()))
    dl: int = int(m.get("DL", 0))
    lb: int = int(m.get("LB", 0))
    db: int = int(m.get("DB", 0))
    grp: str = f"{dl}-{lb}-{db}" if (dl or lb or db) else "UNK"  # e.g., "4-2-5"
    return dl, lb, db, grp

def add_personnel_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rb, te, wr, offg = zip(*df["personnel_off"].map(parse_off_personnel))
    df["off_rb"], df["off_te"], df["off_wr"], df["off_group"] = rb, te, wr, offg
    dl, lb, db, defg = zip(*df["personnel_def"].map(parse_def_personnel))
    df["def_dl"], df["def_lb"], df["def_db"], df["def_group"] = dl, lb, db, defg

    df["off_empty"] = (df["off_rb"] == 0).astype(int)
    df["off_heavy"] = ((df["off_te"] >= 2) | (df["off_rb"] >= 2) | (df["off_wr"] <= 2)).astype(int)
    df["def_nickel"] = (df["def_db"] == 5).astype(int)
    df["def_dime"] = (df["def_db"] >= 6).astype(int)
    return df
data: List[Tuple[str,str]] = [
    ("1 RB, 1 TE, 3 WR", "4 DL, 2 LB, 5 DB"),
    ("2 RB,1 TE,2 WR",   "3 DL,3 LB,5 DB"),
    ("0 RB,0 TE,5 WR",   "2 DL, 4 LB, 5 DB"),
    (None,               None),
]
df: pd.DataFrame = pd.DataFrame(data, columns=["personnel_off","personnel_def"])
off_rb, off_te, off_wr, off_group = zip(*df["personnel_off"].map(parse_off_personnel))
df["off_rb"], df["off_te"], df["off_wr"], df["off_group"] = off_rb, off_te, off_wr, off_group

def_dl, def_lb, def_db, def_group = zip(*df["personnel_def"].map(parse_def_personnel))
df["def_dl"], df["def_lb"], df["def_db"], df["def_group"] = def_dl, def_lb, def_db, def_group

print(df)