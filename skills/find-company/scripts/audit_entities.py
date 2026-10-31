#!/usr/bin/env python3
"""Audit explicitly selected operating and investment organizations without fixed date cutoffs."""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from organizations import select
from investors import cohort


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entity',choices=['organizations','companies','investors'],default='organizations')
    p.add_argument('--wave',choices=['all','first','watchlist','later'],default='all')
    p.add_argument('--category');p.add_argument('--group',choices=['emerging','established'])
    p.add_argument('--status',choices=['confirmed_disclosure','partial','not_found','not_applicable'],help='Applies to operating-organization capital disclosures')
    p.add_argument('--before',type=date.fromisoformat,help='Business-profile check date, not label or channel date')
    p.add_argument('--summary',action='store_true');args=p.parse_args()
    records=select(ROOT,args.entity,args.wave,args.category,args.group)
    records=[(f,r) for f,r in records if (not args.before or date.fromisoformat(r['checked_at'])<args.before) and (not args.status or r.get('investment',{}).get('verification_status')==args.status)]
    if args.summary:
        output={'organizations':len(records),'organization_types':dict(Counter(r['organization_type'] for _,r in records)),'waves':dict(Counter(r['targeting']['wave'] for _,r in records)),'operating_tracks':dict(Counter(r['category_id'] for f,r in records if f=='companies')),'investor_cohorts':dict(Counter(cohort(r) for f,r in records if f=='investors')),'coverage_roles':dict(Counter(r['coverage']['role'] for f,r in records if f=='investors'))}
    else:output=[{'id':r['id'],'name':r['name'],'organization_type':r['organization_type'],'targeting':r['targeting'],'checked_at':r['checked_at'],'json_path':f'data/{f}/{r["id"]}.json'} for f,r in records]
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
