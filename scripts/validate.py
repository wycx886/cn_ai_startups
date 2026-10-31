"""Validate canonical facts, editorial groups, public channels and generated views."""
import argparse
from datetime import date
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlparse
from record_checks import load, record_path, reject_placeholders, schema_validator, today, validate_record

ROOT=Path(__file__).resolve().parents[1]


def iso_day(text):
    return date.fromisoformat(text+('-01-01' if len(text)==4 else '-01' if len(text)==7 else ''))


def validate_data(root=ROOT):
    root=Path(root).resolve()
    platforms=load(root/'data/platforms.json')
    schema_validator('platform-universe.schema.json',root).validate(platforms)
    reject_placeholders(platforms)
    assert len(platforms['platforms'])==len({p['id'] for p in platforms['platforms']}),'Duplicate platform IDs'
    assert iso_day(platforms['checked_at'])<=today(),'Future platform-universe check'
    for p in platforms['platforms']:
        assert iso_day(p['checked_at'])<=iso_day(platforms['checked_at']),'Platform check is after universe date'
    tax=load(root/'data/taxonomy.json')
    schema_validator('taxonomy.schema.json',root).validate(tax)
    categories=[c['id'] for c in tax['categories']]
    assert len(categories)==len(set(categories)),'Duplicate category IDs'
    assert iso_day(tax['version'])<=today(),'Future taxonomy revision'
    all_records=[]
    for folder,kind in [('companies','operating_organization'),('investors','investment_firm')]:
        records=[]
        for path in sorted((root/'data'/folder).glob('*.json')):
            assert record_path(root,kind,path.stem)==path,'Invalid canonical path'
            r=load(path);validate_record(r,root);records.append(r);all_records.append(r)
            assert r['id']==path.stem and r['organization_type']==kind,'Record identity does not match its canonical path'
            assert len(r['aliases'])==len(set(r['aliases'])),'Duplicate aliases'
            if folder=='companies':assert r['category_id'] in categories,'Unknown category'
            else:
                if r['founded']['year'] is not None:assert r['founded']['year']<=iso_day(r['checked_at']).year,'Future foundation year'
                sources={s['id']:s for s in r['sources']}
                for case in r['representative_cases']:
                    assert set(case['evidence_source_ids'])<=sources.keys(),'Case refers to missing evidence'
                    assert all(sources[s].get('scope','organization')=='organization' for s in case['evidence_source_ids']),'Channel-only evidence cannot establish investment cases'
            for source in r['sources']:
                if source['published_date']:assert iso_day(source['published_date'])<=iso_day(source['checked_at']),'Publication is after the claimed check'
                assert urlparse(source['url']).hostname,'Invalid source URL'
            if r['contacts']['other_email']:assert r['contacts']['other_email_purpose'],'Other email needs its purpose'
            if folder=='companies' and (not r['contacts']['careers_url'] or not r['contacts']['recruitment_email']):assert r['notes'],'Missing contacts require scope notes'
        assert records,'Empty organization dataset: '+folder
        assert len(records)==len({r['id'] for r in records}),'Duplicate entity IDs'
        assert len(records)==len({r['name'] for r in records}),'Duplicate entity names'
        if folder=='companies':assert len(records)==len({r['provenance']['original_name'] for r in records}),'Duplicate imported identity'
        print('Validated %d %s and %d source records.'%(len(records),folder,sum(len(r['sources']) for r in records)))
    return all_records


def validate_links(root=ROOT):
    root=Path(root).resolve()
    paths=[root/'AGENTS.md',root/'README.md']
    for folder in ('docs','templates','skills','catalog'):paths.extend(sorted((root/folder).rglob('*.md')))
    for path in paths:
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('https://','http://','mailto:','#')):continue
            resolved=(path.parent/unquote(target.split('#',1)[0])).resolve()
            assert root==resolved or root in resolved.parents,'Local link escapes shared repository'
            assert resolved.exists(),'Broken local link: '+str(path.relative_to(root))+' -> '+target


def validate_indexes(root=ROOT):
    root=Path(root).resolve()
    for entity,index in [('companies','index.json'),('investors','investor-index.json'),('organizations','targets.json')]:
        for entry in load(root/'data'/index)[entity]:
            for field in ('json_path','markdown_path'):
                path=(root/entry[field]).resolve()
                assert root in path.parents and path.is_file(),'Broken machine-index path: '+entry[field]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check-generated',action='store_true');args=p.parse_args()
    records=validate_data()
    if args.check_generated:
        subprocess.run([sys.executable,str(ROOT/'scripts/build.py'),'--check'],check=True)
        validate_indexes()
    validate_links()
    print('Editorial first-wave candidates: %d; no placeholder or draft records accepted.'%sum(r['targeting']['wave']=='first' for r in records))
if __name__=='__main__':main()
