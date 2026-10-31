#!/usr/bin/env python3
"""Audit evidence-linked channels; export neutral collector batches without personal priorities."""
import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from organizations import select
from record_checks import PLATFORMS


def has_layer(record, layer):
    return any(c['layer']==layer and c['verification_status']=='confirmed' for c in record.get('channels',[]))


def has_platform(record):
    return has_layer(record,'recruitment_platform')


def has_social(record):
    return has_layer(record,'professional_social')


def legacy_platform_reference(record):
    urls=[s['url'] for s in record['sources']]+[record['contacts']['careers_url'] or '']
    return any(any((urlsplit(url).hostname or '').lower()==domain or (urlsplit(url).hostname or '').lower().endswith('.'+domain) for domain,_ in PLATFORMS.values()) for url in urls)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entity',choices=['organizations','companies','investors'],default='organizations')
    p.add_argument('--wave',choices=['all','first','watchlist','later'],default='first')
    p.add_argument('--category');p.add_argument('--missing-layer',choices=['official','recruitment_platform','professional_social'])
    p.add_argument('--offset',type=int,default=0);p.add_argument('--limit',type=int)
    p.add_argument('--summary',action='store_true');p.add_argument('--template',action='store_true')
    p.add_argument('--platform',choices=list(PLATFORMS),default='boss_zhipin')
    args=p.parse_args()
    if args.offset<0 or (args.limit is not None and args.limit<1):p.error('Use a nonnegative offset and positive limit')
    records=select(ROOT,args.entity,args.wave,args.category)
    if args.missing_layer:records=[(f,r) for f,r in records if not has_layer(r,args.missing_layer)]
    records=records[args.offset:None if args.limit is None else args.offset+args.limit]
    if args.summary:
        output={'organizations':len(records),'confirmed_structured_channels':{layer:sum(has_layer(r,layer) for _,r in records) for layer in ['official','recruitment_platform','professional_social']},'legacy_contact_fields':{field:sum(bool(r['contacts'][field]) for _,r in records) for field in ['website','careers_url','recruitment_email','other_email']},'legacy_platform_references_pending_structuring':sum(legacy_platform_reference(r) and not has_platform(r) for _,r in records),'note':'Legacy fields/source-domain mentions are not counted as confirmed structured channel ownership.'}
    elif args.template:
        output={'schema_version':1,'public_only':True,'entries':[{'entity_type':r['organization_type'],'entity_id':r['id'],'platform':args.platform,'url':None,'observed_name':None,'checked_at':None,'evidence_title':None,'verification_status':'unverified'} for _,r in records]}
    else:output=[{'entity_type':r['organization_type'],'entity_id':r['id'],'name':r['name'],'channels':r['channels'],'legacy_careers_url':r['contacts']['careers_url']} for _,r in records]
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
