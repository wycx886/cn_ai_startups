"""Read selected company or investor records without loading the whole corpus into an Agent."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--entity',choices=['companies','investors'],default='companies')
 parser.add_argument('--group',choices=['emerging','established'],help='Investor institution group')
 parser.add_argument('--id',help='Stable entity ID, for example hypershell or qiming')
 parser.add_argument('--category',help='Category ID, for example 09')
 parser.add_argument('--text',help='Case-insensitive substring across all recorded fields')
 parser.add_argument('--json',action='store_true',help='Return complete selected JSON records')
 args=parser.parse_args()
 if args.category and args.entity!='companies':parser.error('--category applies to companies')
 if args.group and args.entity!='investors':parser.error('--group applies to investors')
 index=json.loads((ROOT/('data/index.json' if args.entity=='companies' else 'data/investor-index.json')).read_text());selected=[]
 for c in index[args.entity]:
  if args.id and c['id']!=args.id:continue
  if args.category and c['category_id']!=args.category:continue
  if args.group and c['group']!=args.group:continue
  record=None
  if args.text or args.json:record=json.loads((ROOT/c['json_path']).read_text())
  if args.text and args.text.casefold() not in json.dumps(record,ensure_ascii=False).casefold():continue
  selected.append(record if args.json else {k:c[k] for k in (['id','name','category_id','focus','json_path'] if args.entity=='companies' else ['id','name','group','cohort','coverage_role','focus','json_path'])})
 print(json.dumps(selected,ensure_ascii=False,indent=2))
 if not selected:raise SystemExit(1)
if __name__=='__main__':main()
