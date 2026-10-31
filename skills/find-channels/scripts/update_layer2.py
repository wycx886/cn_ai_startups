#!/usr/bin/env python3
"""Update company records from verified public Layer 2 observations, without a private workspace."""
import argparse
import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from record_writes import apply_changes
from record_checks import load, platform_url, record_path, reject_placeholders, schema_validator, today, validate_record


def normalized_name(value):
    return ''.join(c for c in unicodedata.normalize('NFKC',value).casefold() if c.isalnum())


def plan_changes(batch, root=ROOT):
    errors=list(schema_validator('channel-batch.schema.json',root).iter_errors(batch))
    if errors:raise ValueError('Invalid public batch: '+ '; '.join(str(list(e.path))+' '+e.message for e in errors))
    reject_placeholders(batch,'batch')
    planned={};originals={};seen=set()
    for entry in batch['entries']:
        target=record_path(root,entry['entity_type'],entry['entity_id'])
        if not target.is_file():raise ValueError('Unknown organization ID; do not silently discard rows')
        if target not in planned:
            originals[target]=target.read_bytes();planned[target]=json.loads(originals[target])
        record=planned[target]
        if record['id']!=entry['entity_id'] or record['organization_type']!=entry['entity_type']:
            raise ValueError('Record identity does not match the declared organization')
        if normalized_name(entry['observed_name']) not in {normalized_name(n) for n in [record['name'],*record['aliases']]}:
            raise ValueError('Observed organization name does not match a known name/alias; review identity first')
        if '@' in entry['evidence_title'] or re.search(r'(?<!\d)1[3-9]\d{9}(?!\d)',entry['evidence_title']):
            raise ValueError('Evidence title must be a public company-page title without personal contact details')
        observed=date.fromisoformat(entry['checked_at'])
        if observed>today():raise ValueError('A channel check cannot be in the future')
        url=platform_url(entry['url'],entry['platform'])
        key=(entry['entity_type'],entry['entity_id'],entry['platform'],url)
        if key in seen:raise ValueError('Duplicate organization/platform URL in the same batch')
        seen.add(key)
        channel=next((c for c in record['channels'] if c['platform']==entry['platform'] and c['url']==url),None)
        if channel and observed<date.fromisoformat(channel['checked_at']):raise ValueError('Stale observation would downgrade a newer channel check')
        source=next((s for s in record['sources'] if s.get('scope')=='channel' and s['url']==url),None)
        if source and observed<date.fromisoformat(source['checked_at']):raise ValueError('Stale observation would downgrade newer source evidence')
        if source is None:
            numbers=[int(s['id'][1:]) for s in record['sources']]
            source={'id':'s%02d'%(max(numbers,default=0)+1),'scope':'channel','title':entry['evidence_title'],'url':url,'supports':'公开企业主页主体：'+entry['observed_name']+'；只核验入口归属，不表示具体岗位开放。','published_date':None,'checked_at':entry['checked_at']}
            record['sources'].append(source)
        else:
            source.update(title=entry['evidence_title'],checked_at=entry['checked_at'])
        replacement={'id':channel['id'] if channel else 'ch-'+hashlib.sha256((entry['platform']+'\n'+url).encode()).hexdigest()[:16],
                     'layer':'recruitment_platform','platform':entry['platform'],'url':url,'purpose':'recruitment',
                     'owner':{'scope':'organization','name':record['name'],'role':None},'verification_status':'confirmed',
                     'checked_at':entry['checked_at'],'source_ids':[source['id']],'notes':None}
        if channel:channel.update(replacement)
        else:record['channels'].append(replacement)
    # Validate the whole batch before any write; business facts/dates and legacy contacts are unchanged.
    changes={}
    for target,record in planned.items():
        validate_record(record,root)
        text=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode()
        if text!=originals[target]:changes[target]=(originals[target],text)
    return changes




def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch-file',default='-',help='Public observations JSON; default - reads standard input without saving a batch file')
    flags=p.add_mutually_exclusive_group();flags.add_argument('--apply',action='store_true');flags.add_argument('--dry-run',action='store_true',help='Explicit preview; also the default')
    args=p.parse_args()
    if args.batch_file=='-':
        if sys.stdin.isatty():p.error('Pipe public observations as JSON or provide --batch-file PATH')
        batch=json.load(sys.stdin)
    else:batch=load(Path(args.batch_file).expanduser())
    changes=plan_changes(batch,ROOT)
    summary={'dry_run':not args.apply,'updated_records':[{'file':p.relative_to(ROOT.resolve()).as_posix(),'channel_count':len(json.loads(content)['channels'])} for p,(_,content) in changes.items()],
             'business_profile_dates_changed':False,'legacy_contacts_changed':False,'note':'Input asserts a public page observation; this tool validates the record contract, not the truth of a remote webpage. Review identity/evidence before --apply.'}
    if args.apply:apply_changes(changes)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
