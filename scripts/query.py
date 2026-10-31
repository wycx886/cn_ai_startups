"""Query public organizations; first-wave selection is explicit and independent of personal preferences."""
import argparse
import json
from organizations import select
from corporate import FORMS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entity', choices=['organizations','companies','investors'], default='organizations')
    p.add_argument('--wave', choices=['all','first','watchlist','later'], default='all')
    p.add_argument('--player-group', choices=['new_entrant','incumbent','unresolved'])
    p.add_argument('--group', choices=['emerging','established'])
    p.add_argument('--id')
    p.add_argument('--category')
    p.add_argument('--text')
    p.add_argument('--form', choices=list(FORMS), help='Explicitly classified organization form; missing values are unknown')
    p.add_argument('--parent', help='Parent platform ID from data/platforms.json')
    p.add_argument('--json', action='store_true', help='Return complete selected records')
    args=p.parse_args();results=[]
    for folder,r in select(entity=args.entity,wave=args.wave,category=args.category,group=args.group,player_group=args.player_group,form=args.form,parent=args.parent):
        if args.id and r['id']!=args.id:continue
        if args.text and args.text.casefold() not in json.dumps(r,ensure_ascii=False).casefold():continue
        results.append(r if args.json else {'id':r['id'],'name':r['name'],'organization_type':r['organization_type'],'player_group':r['targeting']['player_group'],'wave':r['targeting']['wave'],'organizational_context':r.get('organizational_context'),'focus':r['focus'],'json_path':f'data/{folder}/{r["id"]}.json'})
    print(json.dumps(results,ensure_ascii=False,indent=2))
    if not results:raise SystemExit(1)
if __name__=='__main__':main()
