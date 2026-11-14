#!/usr/bin/env python3
"""Derive manuscript TeX tables and a primary contrast figure from shipped CSVs."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
P=R/'paper'
W=pd.read_csv(R/'results/joint_trend_windows.csv')
A=W[W.regime=='year_stratified']
G=W[W.regime=='global']
keys=['window','metric','target_a','target_b']
assert A.set_index(keys).joint_state.equals(G.set_index(keys).joint_state)
assert len(A)==90
def tt(name, rows):
    (P/name).write_text(''.join(' & '.join(map(str,r))+' '+chr(92)*2+'\n' for r in rows)+chr(92)+'bottomrule\n')
C=pd.read_csv(R/'source/canonical_independent.csv').sort_values('scale',ascending=False)
tt('tab_canonical.tex',[[x.target,int(x.scale),f'{100*x.trend_ols:.2f}',f'{100*x.trend_theilsen:.2f}',
    f'{x.citation_ratio:.3f}',f'{x.citation_ratio_loo:.3f}',f'{x.citation_percentile:.3f}',
    f'{x.top10_share:.3f}'] for x in C.itertuples()])
tt('tab_directions.tex',[[w.replace('_','--'),m,n] for w in A.window.unique()
    for m,k in [('OLS','trend_ols'),('Theil--Sen','trend_theilsen')]
    for n in [sum(A.loc[(A.window==w)&(A.metric==k),'joint_state']!='UNRESOLVED')]])
D=pd.read_csv(R/'results/joint_trend_reversals.csv')
B=D[(D.regime=='year_stratified')&D.descriptive_reversal].fillna('')
def fmt(x):
    return x.replace('_','--').replace('|',', ') if x else '---'
tt('tab_reversals.tex',[[('OLS' if x.metric=='trend_ols' else 'Theil--Sen'),x.target_a+'/'+x.target_b,
    fmt(x.descriptive_positive),fmt(x.descriptive_negative),fmt(x.supported_positive or x.supported_negative)]
    for x in B.itertuples()])
fig,ax=plt.subplots(1,2,figsize=(10.0,3.0),sharey=True)
for a,name in zip(ax,['Europa','Venus']):
    zz=A[(A.target_a=='Enceladus')&(A.target_b==name)&(A.metric=='trend_ols')]
    for i,x in enumerate(zz.itertuples()):
        y=2-i
        a.plot([x.band_envelope_min_pp,x.band_envelope_max_pp],[y,y],color='#8d97a5',lw=2)
        a.plot([x.estimate_min_pp,x.estimate_max_pp],[y,y],color='#005e87',lw=6,solid_capstyle='butt')
    a.axvline(0,color='0.25',ls='--',lw=.8)
    a.set_yticks([2,1,0],['2000–2023','2010–2023','2019–2023'])
    a.set_ylim(-.55,2.55)
    a.set_xlabel('OLS growth contrast (percentage points)')
    a.set_title('Enceladus minus '+name)
    a.spines[['top','right']].set_visible(False)
fig.tight_layout()
fig.savefig(P/'figures/joint_trends.pdf')
