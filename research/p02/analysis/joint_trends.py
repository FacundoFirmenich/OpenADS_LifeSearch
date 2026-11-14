#!/usr/bin/env python3
"""Reproduce archived trends, then calibrate joint real-paper bootstrap bands."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import sparse
import p02_pipeline as p

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'source'
OUT = ROOT / 'results'
TARGETS = p.TARGETS
PAIRS = list(itertools.combinations(range(6), 2))
DEN = np.array(PAIRS).T
RETS = ['inclusive', 'curated_gaia', 'strict_text']
ATTS = ['full', 'target_split']
TEAMS = ['unit', 'reciprocal_legacy', 'reciprocal_exclude_missing', 'reciprocal_impute']
METRICS = ['trend_ols', 'trend_theilsen']

def sha(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()

def trend(annual, lo, hi):
    years = np.arange(lo, hi + 1)
    zz = np.log1p(annual[..., lo - 2000:hi - 1999])
    cx = years - years.mean()
    ss = zz @ (cx / (cx @ cx))
    a, b = np.triu_indices(len(years), 1)
    ts = np.median((zz[..., b] - zz[..., a]) / (years[b] - years[a]), axis=-1)
    return np.expm1(np.stack([ss, ts], axis=-1))

def assemble(df):
    df = df.loc[df.year.between(2000, 2023)].copy()
    papers = df[['bibcode', 'year']].drop_duplicates().sort_values(['year','bibcode'])
    assert len(papers) == 9021 and len(df) == 9762
    bib = dict(zip(papers.bibcode, range(len(papers))))
    tgt = dict(zip(TARGETS, range(len(TARGETS))))
    row, col, data = [], [], []
    for j, (ret, att, team) in enumerate(itertools.product(RETS, ATTS, TEAMS)):
        x = p.add_analysis_weights(df.loc[p.retrieval_mask(df, ret)], att, team)
        row.extend(x.bibcode.map(bib))
        col.extend((j*6 + x.target.map(tgt))*24 + x.year - 2000)
        data.extend(x.weight)
    op = sparse.csr_matrix((data,(row,col)),shape=(len(papers),24*6*24)).T.tocsr()
    return papers.year.to_numpy(), op

def project(op, mult):
    annual = (op @ mult.T).T.reshape(len(mult),24,6,24)
    return np.stack([trend(annual, lo, hi) for lo,hi,_ in p.COMPLETE_WINDOWS],axis=2)

def diff(t):
    return t[..., DEN[0], :] - t[..., DEN[1], :]

def resample(years, op, n, seed, stratified):
    rng=np.random.default_rng(seed)
    groups = [np.flatnonzero(years == yy) for yy in np.unique(years)] if stratified else [np.arange(len(years))]
    out=np.empty((n,24,3,15,2))
    for ii in range(0,n,32):
        m = min(32,n-ii)
        M=np.empty((m,len(years)),dtype=float)
        for idx in groups:
            M[:,idx]=rng.multinomial(len(idx), np.full(len(idx),1/len(idx)),size=m)
        assert sum(M[0]) == len(years)
        out[ii:ii+m]=diff(project(op,M))
    return out

def summarize(draw, est):
    sig=draw.std(axis=0,ddof=1)
    assert (sig>0).all() and np.isfinite(draw).all()
    q=lambda a:float(np.quantile(a,.95,method='higher'))
    m=np.max(np.abs((draw-est)/sig).reshape(len(draw),-1), axis=1)
    crit=q(m)
    return crit,sig,crit*sig, [q(a) for a in np.array_split(m,2)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--draws',type=int,default=10000)
    args=ap.parse_args()
    assert args.draws >= 2
    ref=json.loads((BASE/'input_sha256.json').read_text())
    for k,v in ref.items():
        assert sha(BASE/k)==v,k
    df,_=p.load_and_validate(BASE/'raw')
    years,op=assemble(df)
    estimate=project(op,np.ones((1,len(years))))[0]
    hist = pd.read_csv(BASE/'specifications_reproduced.csv').set_index(['spec_id','target','metric'])
    errors=[]
    for j,w,t,k in itertools.product(range(24),range(3),range(6),range(2)):
        errors.append(abs(estimate[j,w,t,k]-hist.loc[(j*3+w,TARGETS[t],METRICS[k]),'value']))
    assert len(errors)==864 and max(errors)<1e-11
    e=diff(estimate)
    rr=[]; win=[]; rev=[]; run={}
    for name,seed,strat in [('year_stratified',2026111401,True),('global',2026111402,False)]:
        draw=resample(years,op,args.draws,seed,strat)
        crit,sig,rad,half=summarize(draw,e)
        l,u=e-rad,e+rad
        plo,phi=np.quantile(draw,[.025,.975],axis=0)
        run[name]={'draws':args.draws,'seed':seed,'max_critical':crit,
                   'half_run_max_critical':half,'all_contrasts':int(e.size)}
        pos=(l>0); neg=(u<0)
        for j,w,h,k in itertools.product(range(24),range(3),range(15),range(2)):
            a,b=(TARGETS[i] for i in PAIRS[h]); ix=j,w,h,k
            rr.append([name,j*3+w,p.COMPLETE_WINDOWS[w][2],METRICS[k],a,b,
                       *([100*x[ix] for x in [e,sig,l,u,plo,phi]])])
        for w,h,k in itertools.product(range(3),range(15),range(2)):
            sl=np.s_[:,w,h,k]; a,b=(TARGETS[i] for i in PAIRS[h])
            npos,nneg=int(pos[sl].sum()),int(neg[sl].sum())
            win.append([name,p.COMPLETE_WINDOWS[w][2],METRICS[k],a,b,
                        100*e[sl].min(),100*e[sl].max(),100*l[sl].min(),100*u[sl].max(),
                        npos,nneg,'A_GT_B' if npos==24 else 'B_GT_A' if nneg==24 else 'UNRESOLVED',
                        bool(np.all(l[sl]>.02)),bool(np.all(u[sl]<-.02))])
        for h,k in itertools.product(range(15),range(2)):
            a,b=(TARGETS[i] for i in PAIRS[h])
            between=lambda arr: '|'.join(p.COMPLETE_WINDOWS[i][2] for i in np.flatnonzero(arr))
            p1,n1 = (e[:,:,h,k]>0).all(0),(e[:,:,h,k]<0).all(0)
            p2,n2 = pos[:,:,h,k].all(0),neg[:,:,h,k].all(0)
            rev.append([name,METRICS[k],a,b,between(p1),between(n1),between(p2),between(n2),
                        bool(p1.any() and n1.any()),bool(p2.any() and n2.any())])
        del draw
    pd.DataFrame(rr,columns='regime spec_id window metric target_a target_b estimate_pp bootstrap_sd_pp joint_low_pp joint_high_pp percentile_low_pp percentile_high_pp'.split()).to_csv(OUT/'joint_trend_contrasts.csv',index=False)
    pd.DataFrame(win,columns='regime window metric target_a target_b estimate_min_pp estimate_max_pp band_envelope_min_pp band_envelope_max_pp n_joint_positive n_joint_negative joint_state all_positive_beyond_2pp all_negative_beyond_2pp'.split()).to_csv(OUT/'joint_trend_windows.csv',index=False)
    rev=pd.DataFrame(rev,columns='regime metric target_a target_b descriptive_positive descriptive_negative supported_positive supported_negative descriptive_reversal supported_reversal'.split())
    rev.to_csv(OUT/'joint_trend_reversals.csv',index=False)
    assert (rev.groupby('regime').descriptive_reversal.sum()==8).all()
    report={'observed_trend_values_verified':len(errors),'max_abs_error':max(errors),
            'family':'24 x 3 x 15 x 2','regimes':run,
            'supported_reversals':{k:int(v) for k,v in rev.groupby('regime').supported_reversal.sum().items()},
            'scope':'Retrospective bootstrap conditional on legacy ADS corpus; paper-level cluster only; fixed analysis maps.'}
    (OUT/'joint_trends_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__ == '__main__':
    main()
