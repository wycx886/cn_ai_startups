#!/usr/bin/env python3
"""Validate sourced public people observations and update company people[] directly."""
import argparse
from datetime import date
import json
from pathlib import Path
import sys
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlunsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from record_checks import load, record_path, reject_placeholders, schema_validator, today, validate_record
from record_writes import apply_changes
from person_checks import person_profile_url, public_url


def normalized_name(value):
    return ''.join(unicodedata.normalize('NFKC', value).casefold().split())


def evidence_url(url, platform):
    try:
        return person_profile_url(url, platform)
    except ValueError:
        parsed = public_url(url)
        query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
                 if not k.lower().startswith('utm_')]
        return urlunsplit(('https', parsed.hostname.lower(), parsed.path or '/', urlencode(query), ''))


def add_source(record, evidence):
    source = next((s for s in record['sources'] if s.get('scope') == 'person' and s['url'] == evidence['url'] and s['supports'] == evidence['supports']), None)
    if source:
        if evidence['checked_at'] < source['checked_at']:
            raise ValueError('Stale person evidence would downgrade a newer source check')
        source.update(evidence)
    else:
        number = max(int(s['id'][1:]) for s in record['sources']) + 1
        source = {'id': 's%02d' % number, 'scope': 'person', **evidence}
        record['sources'].append(source)
    return source['id']


def plan_person_changes(batch, root=ROOT):
    errors = list(schema_validator('person-batch.schema.json', root).iter_errors(batch))
    if errors:
        raise ValueError('Invalid public person batch: ' + '; '.join(str(list(e.path)) + ' ' + e.message for e in errors))
    reject_placeholders(batch, 'batch')
    originals, planned, seen = {}, {}, set()
    for entry in batch['entries']:
        target = record_path(root, entry['entity_type'], entry['entity_id'])
        if not target.is_file():
            raise ValueError('Unknown organization ID')
        if target not in planned:
            originals[target] = target.read_bytes()
            planned[target] = json.loads(originals[target])
            validate_record(planned[target], root)
        record = planned[target]
        if record['id'] != entry['entity_id'] or record['organization_type'] != entry['entity_type']:
            raise ValueError('Organization identity does not match the batch')
        platform = entry['platform']
        url = person_profile_url(entry['url'], platform)
        name = entry['person_name'].strip()
        if not name:
            raise ValueError('Person name is required')
        key = (entry['entity_id'], normalized_name(name), platform, url)
        if key in seen:
            raise ValueError('Duplicate person/profile in the same batch')
        seen.add(key)
        observed = date.fromisoformat(entry['checked_at'])
        if observed > today():
            raise ValueError('Person/profile check date cannot be in the future')
        people = record.setdefault('people', [])
        person = next((p for p in people if normalized_name(p['name']) == normalized_name(name)), None)
        if person and entry['checked_at'] < person['checked_at']:
            raise ValueError('Stale observation would downgrade newer person identity evidence')
        existing = next((p for p in (person or {}).get('profiles', [])
                         if p['platform'] == platform and person_profile_url(p['url'], platform) == url), None)
        if existing and entry['checked_at'] < existing['checked_at']:
            raise ValueError('Stale observation would downgrade a newer profile check')
        evidence = []
        for item in entry['identity_evidence']:
            checked = date.fromisoformat(item['checked_at'])
            if checked < observed or checked > today():
                raise ValueError('Identity evidence date must support the claimed person check')
            evidence.append({**item, 'url': evidence_url(item['url'], platform)})
        urls = [e['url'] for e in evidence]
        if url in urls or len(urls) != len(set(urls)):
            raise ValueError('Identity evidence must use distinct URLs in addition to the profile itself')
        if platform == 'github':
            api_url = 'https://api.github.com/users/' + url.rsplit('/', 1)[1]
            if entry.get('account_type') != 'User' or api_url not in urls:
                raise ValueError('GitHub personal accounts require observed User type and API evidence')
        evidence.insert(0, {'title': entry['evidence_title'], 'url': url,
                           'supports': '公开专业主页与本次人物身份观察：' + name + '；职务：' + (entry.get('person_role') or '未标明'),
                           'published_date': None, 'checked_at': entry['checked_at']})
        refs = [add_source(record, e) for e in evidence]
        prior_refs = set((person or {}).get('source_ids', [])) | set((existing or {}).get('source_ids', []))
        history = set((person or {}).get('historical_source_ids', [])) | (prior_refs - set(refs))
        facts = {'name': name, 'role': (entry.get('person_role') or '').strip() or None, 'background': (entry.get('background') or '').strip() or None,
                 'previous_firms': entry.get('previous_firms', []), 'checked_at': entry['checked_at'],
                 'source_ids': refs, 'verification_status': 'confirmed', 'notes': entry.get('notes')}
        if person is None:
            person = {**facts, 'profiles': []}
            people.append(person)
        else:
            for field in ('role', 'background', 'previous_firms'):
                if person.get(field) and not facts[field]:
                    raise ValueError('Existing identity facts cannot be cleared implicitly by a profile update')
            person.update(facts)
        if history:
            person['historical_source_ids'] = sorted(history - set(refs))
        profile = {'platform': platform, 'url': url, 'verification_status': 'confirmed',
                   'checked_at': entry['checked_at'], 'source_ids': refs, 'notes': entry.get('notes')}
        if platform == 'github':
            profile['account_type'] = entry['account_type']
        if existing:
            existing.update(profile)
        else:
            person['profiles'].append(profile)
    changes = {}
    for target, record in planned.items():
        validate_record(record, root)
        content = (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        if content != originals[target]:
            changes[target] = (originals[target], content)
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-file', default='-', help='Public observations JSON; default - reads standard input')
    flags = parser.add_mutually_exclusive_group()
    flags.add_argument('--apply', action='store_true')
    flags.add_argument('--dry-run', action='store_true', help='Preview only; also the default')
    args = parser.parse_args()
    if args.batch_file == '-':
        if sys.stdin.isatty():
            parser.error('Pipe verified public JSON or provide --batch-file PATH')
        batch = json.load(sys.stdin)
    else:
        batch = load(Path(args.batch_file).expanduser())
    changes = plan_person_changes(batch, ROOT)
    if args.apply:
        apply_changes(changes)
    print(json.dumps({'dry_run': not args.apply,
                      'updated_records': [{'file': p.relative_to(ROOT.resolve()).as_posix()} for p in changes],
                      'business_profile_dates_changed': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
