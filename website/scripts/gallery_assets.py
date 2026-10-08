"""Keep compact documentation sheets separate from the external gallery assets."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image


def asset_location(assets, root):
    assets = assets.resolve()
    root = root.resolve()
    if assets.is_relative_to(root) and not assets.is_relative_to(root/'website/assets'):
        raise ValueError('Keep full assets outside the checkout or under ignored website/assets/')


def inventory(assets, destination):
    rows=[]
    for folder in ('images', 'comparisons'):
        for path in sorted((assets/folder).rglob('*')):
            if path.is_file() and path.suffix in ('.jpg', '.md', '.json') and not path.name.startswith('._'):
                rows.append(dict(path=path.relative_to(assets).as_posix(), bytes=path.stat().st_size,
                                 sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    destination.write_text(json.dumps(rows, indent=2), encoding='utf-8')
    return rows


def compact_sheets(assets, docs):
    source=assets/'comparisons';target=docs/'comparisons';target.mkdir(parents=True,exist_ok=True)
    rows=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    previous=target/'manifest.json'
    if previous.exists():
        for entry in json.loads(previous.read_text(encoding='utf-8')):
            (target/Path(entry['path']).name).unlink(missing_ok=True)
    for row in rows:
        path=Path(row['path']).name
        shutil.copyfile(source/path,target/path)
    shutil.copyfile(source/'manifest.json',target/'manifest.json')
    text=(source/'README.md').read_text(encoding='utf-8')
    text+='\nFull-size scene previews are available in the [online gallery](https://nikon-recipes-to-lr-profiles.pages.dev/). Website assets are stored separately from this source tree.\n'
    (target/'README.md').write_text(text, encoding='utf-8')
