"""Validate canonical facts, source metadata, local links and generated views."""
import argparse,json,re,subprocess,sys
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import urlparse
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]
TODAY=datetime.now(timezone(timedelta(hours=8))).date()
def load(path):return json.loads(path.read_text())
def validate_schema(path,schema):
 errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(load(path)),key=lambda e:str(list(e.path)))
 if errors:raise ValueError(str(path.relative_to(ROOT))+': '+'; '.join(str(list(e.path))+' '+e.message for e in errors))
def iso_day(text):return date.fromisoformat(text+('-01-01' if len(text)==4 else '-01' if len(text)==7 else ''))
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-generated',action='store_true');args=parser.parse_args()
 company_schema=load(ROOT/'schemas/company.schema.json');taxonomy_schema=load(ROOT/'schemas/taxonomy.schema.json')
 Draft202012Validator.check_schema(company_schema);Draft202012Validator.check_schema(taxonomy_schema)
 taxonomy_path=ROOT/'data/taxonomy.json';validate_schema(taxonomy_path,taxonomy_schema);tax=load(taxonomy_path)
 categories=[c['id'] for c in tax['categories']]
 assert len(categories)==len(set(categories)),'Duplicate category ID'
 assert iso_day(tax['version'])<=TODAY,'Taxonomy version is in the future'
 paths=sorted((ROOT/'data/companies').glob('*.json'));assert paths,'No companies'
 records=[]
 for path in paths:
  validate_schema(path,company_schema);c=load(path);records.append(c)
  assert c['id']==path.stem,'ID does not match filename: '+str(path)
  assert c['category_id'] in categories,'Unknown category: '+c['id']
  assert iso_day(c['checked_at'])<=TODAY,'Future company check: '+c['id']
  ids=[s['id'] for s in c['sources']];assert len(ids)==len(set(ids)),'Duplicate source ID: '+c['id']
  assert len(c['aliases'])==len(set(c['aliases'])),'Duplicate alias: '+c['id']
  for s in c['sources']:
   assert iso_day(s['checked_at'])<=iso_day(c['checked_at']),'Source check is newer than company check: '+c['id']
   if s['published_date']:assert iso_day(s['published_date'])<=iso_day(s['checked_at']),'Source published after claimed check: '+c['id']
   assert urlparse(s['url']).hostname,'Invalid source URL: '+c['id']
  contact=c['contacts']
  if contact['other_email']:assert contact['other_email_purpose'],'Other email has no purpose: '+c['id']
  if not contact['careers_url'] or not contact['recruitment_email']:assert c['notes'],'Missing contact needs a note: '+c['id']
 assert len(records)==len({c['id'] for c in records}),'Duplicate company ID'
 assert len(records)==len({c['provenance']['original_name'] for c in records}),'Duplicate imported identity; review merge'
 if args.check_generated:
  subprocess.run([sys.executable,str(ROOT/'scripts/build.py'),'--check'],check=True)
  for path in [ROOT/'README.md',ROOT/'taxonomy.md',ROOT/'docs/data-model.md',*sorted((ROOT/'companies').glob('*.md'))]:
   for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',path.read_text()):
    if target.startswith(('https://','http://','mailto:','#')):continue
    target=target.split('#',1)[0];resolved=(path.parent/target).resolve()
    assert ROOT==resolved or ROOT in resolved.parents,'Local link escapes repository: '+target
    assert resolved.exists(),'Broken local link: '+str(path.relative_to(ROOT))+' -> '+target
 print('Validated %d companies, %d categories and %d source records.'%(len(records),len(categories),sum(len(c['sources']) for c in records)))
if __name__=='__main__':main()
