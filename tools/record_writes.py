"""Apply validated company updates with concurrency checks and conditional rollback."""
from pathlib import Path
import tempfile


def apply_changes(changes):
    temporary=[];committed=[]
    try:
        for path,(original,content) in changes.items():
            if path.read_bytes()!=original:raise ValueError('Organization record changed since preview; recheck before applying')
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.'+path.name+'.',suffix='.tmp',delete=False) as stream:
                stream.write(content);temporary.append((path,Path(stream.name)))
        for path,temp in temporary:
            if path.read_bytes()!=changes[path][0]:raise ValueError('Concurrent edit detected; batch stopped')
            temp.replace(path);committed.append(path)
    except Exception as error:
        conflicts=[]
        for path in committed:
            try:
                # Another agent may have edited an already-applied record while
                # this batch was in flight. Never restore old bytes over it.
                if path.read_bytes()!=changes[path][1]:
                    conflicts.append(path.name)
                    continue
                path.write_bytes(changes[path][0])
            except OSError:
                conflicts.append(path.name)
        if conflicts:
            raise ValueError('Batch stopped; later external edits were preserved. Review these records before retrying: '+', '.join(conflicts)) from error
        raise
    finally:
        for _,temp in temporary:temp.unlink(missing_ok=True)
