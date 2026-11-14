"""Read-only to the canonical estimates; generate retrospective diagnostics."""
import csv
import json
from collections import Counter

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import joint_trends as j

OUT = j.OUT
WINS = j.p.COMPLETE_WINDOWS
TOL = 1e-9  # percentage points; checked against exact-sign archived cells


def state(lo, hi, tol=TOL):
    return 1 if lo > tol else -1 if hi < -tol else 0


def diagnostic(annual, use_years):
    """Keep true calendar spacing when dropping a year; same fixed paper weights."""
    years = np.array(use_years)
    z = np.log1p(annual[..., years - 2000])
    cx = years - years.mean()
    a, b = np.triu_indices(len(years), 1)
    ols = z @ (cx / (cx @ cx))
    sen = np.median((z[..., b] - z[..., a]) / (years[b] - years[a]), axis=-1)
    return 100 * j.diff(np.expm1(np.stack([ols, sen], axis=-1)))


def output_csv(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    ref = json.loads((j.BASE / "input_sha256.json").read_text())
    for k, v in ref.items():
        assert j.sha(j.BASE / k) == v, k
    df, _ = j.p.load_and_validate(j.BASE / "raw")
    years, op = j.assemble(df)
    annual = (op @ np.ones(len(years))).reshape(24, 6, 24)
    cells = pd.read_csv(OUT / "joint_trend_windows.csv")
    columns = ["window", "metric", "target_a", "target_b"]
    prim = cells[cells.regime == "year_stratified"].set_index(columns)
    other = cells[cells.regime == "global"].set_index(columns)
    assert prim.joint_state.to_dict() == other.joint_state.to_dict()
    pairs = [(j.TARGETS[a], j.TARGETS[b]) for a, b in j.PAIRS]
    grid, labels = np.zeros((15, 6), dtype=int), np.empty((15, 6), dtype=object)
    cases, dropped, disjoint = [], [], []
    for w, (start, end, win) in enumerate(WINS):
        full = list(range(start, end + 1))
        base = diagnostic(annual, full)
        removals = {yy: diagnostic(annual, [x for x in full if x != yy]) for yy in full}
        for h, (a, b) in enumerate(pairs):
            for k, metric in enumerate(j.METRICS):
                r = prim.loc[(win, metric, a, b)]
                x = base[:, h, k]
                assert np.allclose([x.min(), x.max()], [r.estimate_min_pp, r.estimate_max_pp], atol=1e-10)
                desc = state(x.min(), x.max())
                assert desc == state(x.min(), x.max(), 0)
                joint = {"A_GT_B": 1, "B_GT_A": -1, "UNRESOLVED": 0}[r.joint_state]
                assert not joint or desc == joint
                tag = 0 if not desc else 2 if joint else 1
                grid[h, w*2+k] = tag
                labels[h, w*2+k] = {1: "A", -1: "B", 0: "-"}[desc] + ("*" if joint else "")
                year_states = {}
                delta = {}
                for yy, y in removals.items():
                    z = y[:, h, k]
                    year_states[yy] = state(z.min(), z.max())
                    delta[yy] = float(max(abs(z - x)))
                    dropped.append(dict(window=win, metric=metric, target_a=a, target_b=b, dropped_year=yy,
                                        minimum_pp=z.min(), maximum_pp=z.max(), sign=year_states[yy],
                                        max_shift_pp=delta[yy]))
                cases.append(dict(window=win, metric=metric, target_a=a, target_b=b, descriptive_sign=desc,
                                  joint_sign=joint, survives_every_year_deletion=bool(desc and all(v == desc for v in year_states.values())),
                                  changed_years=";".join(str(y) for y,v in year_states.items() if v != desc),
                                  largest_shift_pp=max(delta.values())))
    partitions = [(2000, 2009), (2010, 2018), (2019, 2023)]
    parts = [diagnostic(annual, list(range(s,e+1))) for s,e in partitions]
    switched = 0
    for h, (a,b) in enumerate(pairs):
        for k, metric in enumerate(j.METRICS):
            signs=[]
            for (s,e), arr in zip(partitions,parts):
                x=arr[:,h,k]
                signs.append(state(x.min(),x.max()))
                disjoint.append(dict(window=f"{s}_{e}",metric=metric,target_a=a,target_b=b,
                                     minimum_pp=x.min(),maximum_pp=x.max(),sign=signs[-1]))
            switched += {-1,1}.issubset(signs)
    assert len(cases)==90 and len(dropped)==1290 and len(disjoint)==90
    assert (grid == 2).sum() == 16
    output_csv("v44_direction_map.csv",cases)
    output_csv("v44_year_influence.csv",dropped)
    output_csv("v44_disjoint_windows.csv",disjoint)
    c=Counter(("joint" if r["joint_sign"] else "unanimous_only" if r["descriptive_sign"] else "mixed",
               r["survives_every_year_deletion"]) for r in cases)
    summary={"cells":len(cases),"deletion_checks":len(dropped),
             "counts":{"|".join(map(str,k)):v for k,v in sorted(c.items())},
             "short_unanimous":sum(bool(r["descriptive_sign"]) for r in cases if r["window"]=="2019_2023"),
             "short_unanimous_stable_under_all_deletions":sum(r["survives_every_year_deletion"] for r in cases if r["window"]=="2019_2023"),
             "disjoint_descriptive_reversal_pairs_by_estimator":int(switched),
             "status":"Descriptive sensitivity only; not a hypothesis test or coverage validation"}
    (OUT/"v44_temporal_receipt.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    fig,ax=plt.subplots(figsize=(6.5,6.2))
    colors=["#f0f0ee","#e7b76b","#305e71"]
    ax.imshow(grid,aspect="auto",cmap=ListedColormap(colors),vmin=0,vmax=2)
    for h in range(15):
        for col in range(6):
            ax.text(col,h,labels[h,col],ha="center",va="center",fontsize=9,
                    color="white" if grid[h,col]==2 else "#171a21",
                    weight="bold" if grid[h,col]==2 else "normal")
    ax.set_xticks(range(6),["OLS","Theil-Sen"]*3)
    ax.xaxis.tick_top()
    ax.set_yticks(range(15),[f"{a} / {b}" for a,b in pairs])
    ax.tick_params(length=0,labelsize=8)
    for i, title in enumerate(["2000-2023","2010-2023","2019-2023"]):
        ax.text((i*2+1)/6,1.09,title,transform=ax.transAxes,ha="center",fontsize=10,weight="bold")
    ax.set_xticks(np.arange(-.5,6,1),minor=True)
    ax.set_yticks(np.arange(-.5,15,1),minor=True)
    ax.grid(which="minor",color="white",linewidth=0.9)
    ax.tick_params(which="minor",bottom=False,left=False)
    for b in [1.5,3.5]:
        ax.axvline(b,color="white",linewidth=2.5)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.legend(handles=[Patch(facecolor=color,label=label) for color,label in zip(
        colors,["No unanimous sign","Unanimous only","Joint support (*)"])],
        loc="upper center",bbox_to_anchor=(0.50,-0.024),frameon=False,ncol=3,fontsize=8)
    fig.subplots_adjust(left=.27,right=.98,bottom=.095,top=.88)
    fig.savefig(j.ROOT/"paper/figures/direction_map.pdf",bbox_inches="tight",pad_inches=.09)
    plt.close(fig)


if __name__ == "__main__":
    main()
