#!/usr/bin/env python3
"""Draw an auditable unlabeled sample for precision of historical assignments."""
from collections import defaultdict
import csv
import hashlib
import json
import re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SEED='P02-20261114-precision-pilot-v1'
groups=defaultdict(list)
with (R/'source/raw/all_papers_raw_concat.csv').open(newline='',encoding='utf-8-sig') as f:
    for x in csv.DictReader(f):
        y=int(x['pubdate'][:4])
        if not 2000<=y<=2023: continue
        target=x['target']
        keywords=json.loads(x['keyword'] or '[]') or []
        kw=' '.join(str(x) for x in keywords)
        explicit=re.search(r'\b'+re.escape(target)+r'\b', x['title']+' '+kw,re.I)
        key=(target,'2000–2009' if y<2010 else '2010–2018' if y<2019 else '2019–2023',
             'name_present' if explicit else 'name_not_present')
        groups[key].append(x)
assert sum(map(len,groups.values()))==9762
assert len(groups)==36
public=[]; keys=[]
for key, rows in sorted(groups.items()):
    n=min(20,len(rows))
    def h(x): return hashlib.sha256('|'.join([SEED,x['target'],x['bibcode']]).encode()).hexdigest()
    for x in sorted(rows,key=h)[:n]:
        ident=h(x)[:20]
        public.append((ident,x['target'],x['bibcode'],x['pubdate'],x['title']))
        keys.append((ident,*key,len(rows),n,n/len(rows)))
assert len({r[0] for r in public})==len(public)==len(keys)
for path, header, rows in [
    ('retrieval_coder_packet.csv',['id','target','bibcode','archive_date','title'],public),
    ('retrieval_sampling_key.csv',['id','target','period','title_keyword_stratum','N_h','n_h','inclusion_probability'],keys)]:
    with (R/'results'/path).open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(header); w.writerows(sorted(rows))
print(len(public),'assignments;',len({r[2] for r in public}),'distinct bibcodes; 36 strata; zero human labels')
