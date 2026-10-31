#!/usr/bin/env python3
"""Prepare an explicitly unverified private research draft; never write canonical data."""
import argparse
import json
from pathlib import Path
import sys
import unicodedata
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from record_checks import ID_PATTERN
sys.path.insert(0,str(ROOT/'skills/setup-workspace/scripts'))
from workspace import workspace_path


def normalized(value):
    return ''.join(unicodedata.normalize('NFKC',value).casefold().split())


def make_draft(root, entity, entity_id, name, category=None, group='emerging', player_group='unresolved'):
    if not ID_PATTERN.fullmatch(entity_id):raise ValueError('Use a lowercase ASCII stable ID')
    if player_group not in {'new_entrant','incumbent','unresolved'}:raise ValueError('Unknown player group')
    folder='companies'
    for path in (Path(root)/'data'/folder).glob('*.json'):
        r=json.loads(path.read_text())
        if r['id']==entity_id or normalized(name) in {normalized(n) for n in [r['name'],*r['aliases']]}:
            raise ValueError('Organization ID or name already exists; update the existing record')
    if entity=='company':
        categories={r['id'] for r in json.loads((Path(root)/'data/taxonomy.json').read_text())['categories']}
        if category not in categories:raise ValueError('Choose an existing taxonomy category')
    kind='operating_organization' if entity=='company' else 'investment_firm'
    r={'schema_version':2,'organization_type':kind,'id':entity_id,'name':name,'aliases':[],
       'targeting':{'kind':'editorial_assessment','player_group':player_group,'wave':'later' if player_group=='incumbent' else 'watchlist','rationale':None,'source_ids':[],'labelled_at':None},
       'channels':[],'contacts':{k:None for k in ['website','careers_url','recruitment_email','other_email','other_email_purpose']},
       'checked_at':None,'sources':[],'notes':None}
    if entity=='company':r.update(category_id=category,focus=None,products=None,locations_text=None,comparison={'kind':'editorial_analysis','summary':None,'peer_names':[]},investment={'summary':None,'verification_status':None},provenance={'original_name':name,'original_track':category,'original_subtrack':'新增研究候选'})
    else:r.update(group=group,founded={'year':None,'basis':None},team=[],focus=None,stage=None,representative_cases=[],recent_activity=None,why_follow=None,difference=None,coverage={'role':'watchlist','reason':None})
    return {'draft':True,'entity_type':kind,'research_required':['主体、组织形态与归属','业务或投资策略','来源与实际核查日期','新进／已有及圈选依据','资本披露与案例归因'],'record':r}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entity',choices=['company','investor'],required=True);p.add_argument('--id',required=True);p.add_argument('--name',required=True)
    p.add_argument('--category');p.add_argument('--group',choices=['emerging','established'],default='emerging')
    p.add_argument('--player-group',choices=['new_entrant','incumbent','unresolved'],default='unresolved',help='Provisional draft classification, not a factual verification')
    group=p.add_mutually_exclusive_group();group.add_argument('--save-draft',action='store_true');group.add_argument('--dry-run',action='store_true',help='Compatibility alias for the default stdout-only behavior')
    args=p.parse_args();draft=make_draft(ROOT,args.entity,args.id,args.name,args.category,args.group,args.player_group)
    text=json.dumps(draft,ensure_ascii=False,indent=2)+'\n'
    if args.save_draft:
        ws=workspace_path(ROOT)
        if not ws.is_dir():raise SystemExit('Initialize or bind a private workspace before saving a draft')
        folder=ws/'drafts/research'
        if any(p.is_symlink() for p in [folder,folder.parent]):raise SystemExit('Draft directory must not be linked to shared storage')
        folder.mkdir(parents=True,exist_ok=True)
        target=folder/(args.entity+'-'+args.id+'.json')
        with target.open('x',encoding='utf-8') as output:output.write(text)
        print('Saved an unverified draft in the configured private workspace; no canonical data changed.')
    else:print(text,end='')
if __name__=='__main__':main()
