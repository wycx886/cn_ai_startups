"""Read selected company records without loading the whole corpus into an Agent."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--id',help='Stable company ID, for example hypershell')
 parser.add_argument('--category',help='Category ID, for example 09')
 parser.add_argument('--text',help='Case-insensitive substring across all recorded fields')
 parser.add_argument('--json',action='store_true',help='Return complete selected JSON records')
 args=parser.parse_args();index=json.loads((ROOT/'data/index.json').read_text());selected=[]
 for c in index['companies']:
  if args.id and c['id']!=args.id:continue
  if args.category and c['category_id']!=args.category:continue
  record=None
  if args.text or args.json:record=json.loads((ROOT/c['json_path']).read_text())
  if args.text and args.text.casefold() not in json.dumps(record,ensure_ascii=False).casefold():continue
  selected.append(record if args.json else {k:c[k] for k in ['id','name','category_id','focus','json_path']})
 print(json.dumps(selected,ensure_ascii=False,indent=2))
 if not selected:raise SystemExit(1)
if __name__=='__main__':main()
