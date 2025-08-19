from pathlib import Path

import mkdocs_gen_files
from mkdocs_gen_files.nav import Nav

nav = Nav()

_here: Path = Path(__file__).resolve().parent
_src_dir: Path = _here.parent / 'src'


for path in sorted(_src_dir.rglob('*.py')):
    _mod_path = path.relative_to(_src_dir).with_suffix('')
    _doc_path = path.relative_to(_src_dir).with_suffix('.md')
    _full_path = Path('reference', _doc_path)

    parts = tuple(_mod_path.parts)
    if '__pycache__' in parts:
        continue

    if parts[-1] == '__init__':
        parts = parts[:-1]
        _doc_path = _doc_path.with_name('index.md')
        _full_path = Path('reference', _doc_path)
    elif parts[-1].startswith('_'):
        pass
    if not parts:
        continue

    nav[parts] = _doc_path.as_posix()
    with mkdocs_gen_files.open(_full_path, 'w') as fd:
        ident = '.'.join(parts)
        if parts[-1] in ('_core', '_exceptions'):
            module_name = parts[-1].lstrip('_')
            print(f'# {module_name.title()}', file=fd)
            print(file=fd)

        print(f'::: {ident}', file=fd)

    mkdocs_gen_files.set_edit_path(_full_path, path)

with mkdocs_gen_files.open('reference/SUMMARY.md', 'w') as nav_file:
    nav_file.writelines(nav.build_literate_nav())
