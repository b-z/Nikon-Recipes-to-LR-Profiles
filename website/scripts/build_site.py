"""Build a static gallery from external assets; never write images into docs/."""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from build_gallery import build_pages
from gallery_assets import asset_location


def main():
    root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assets', type=Path, default=os.environ.get('NIKON_LR_WEBSITE_ASSETS'))
    p.add_argument('--output', type=Path, default=root / 'website/dist')
    args = p.parse_args()
    if not args.assets or not args.assets.is_dir():
        p.error('Supply --assets or NIKON_LR_WEBSITE_ASSETS: an extracted website asset pack')
    asset_location(args.assets, root)
    if args.output.resolve().is_relative_to(root) and not args.output.resolve().is_relative_to(root/'website/dist'):
        p.error('In-checkout output must be under ignored website/dist/')
    if args.output.exists() and any(args.output.iterdir()):
        p.error('Output must be empty; use a new build directory')
    if args.output.resolve() == args.assets.resolve():
        p.error('Output must differ from assets')
    docs = root / 'docs'
    data = root / 'website/data'
    inventory = json.loads((data / 'assets_manifest.json').read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    # Documentation stays light in Git; the site receives full-size assets below.
    paths = [f for f in docs.rglob('*') if f.is_file() and f.suffix in ('.md', '.json', '.jpg')]
    paths += [root / name for name in ('LICENSE', 'PROFILE_LICENSE.md', 'THIRD_PARTY_NOTICES.md', 'samples/LICENSE.md')]
    for source in paths:
        destination = args.output / source.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    for source in data.glob('*.json'):
        shutil.copyfile(source, args.output / 'docs' / source.name)
        alias = args.output / 'website/data' / source.name
        alias.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, alias)
    shutil.copyfile(root/'website/README.md', args.output/'website/README.md')
    # Stream each asset once, verifying hashes while copying. Fail on stale packs.
    for row in inventory:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] not in ('images', 'comparisons'):
            raise ValueError('Unsafe asset path')
        if relative.suffix not in ('.jpg', '.json', '.md'):
            raise ValueError('Unexpected asset type')
        source = args.assets / relative
        if not source.resolve().is_relative_to(args.assets.resolve()):
            raise ValueError('Asset leaves its directory')
        destination = args.output / 'docs' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256()
        with source.open('rb') as inp, destination.open('wb') as out:
            for block in iter(lambda: inp.read(1024**2), b''):
                h.update(block); out.write(block)
        if h.hexdigest() != row['sha256'] or destination.stat().st_size != row['bytes']:
            raise ValueError('Asset checksum mismatch: ' + row['path'])
    rows = json.loads((docs / 'recipe_metrics.json').read_text())
    refs = json.loads((data / 'nx_references.json').read_text())
    for row in rows:
        for stem in ('9046', '2849', '2694', '5054'):
            if not (args.output / 'docs/images' / f'{stem}_{row["recipe"]}.jpg').is_file():
                raise ValueError('Missing conversion preview')
        if not (args.output / 'docs/images/thumbs' / f'{row["recipe"]}.jpg').is_file():
            raise ValueError('Missing recipe thumbnail')
    for ref in refs:
        if not (args.output / 'docs' / ref['path']).is_file():
            raise ValueError('Missing NX reference')
    build_pages(rows, args.output / 'docs')
    (args.output / '_redirects').write_text('/ /docs/gallery.html 302\n/gallery /docs/gallery.html 302\n')
    (args.output / '_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
    files = [f for f in args.output.rglob('*') if f.is_file()]
    forbidden = {'.nef', '.np3', '.ncp', '.nksc', '.tif', '.tiff', '.toml', '.env'}
    if any(f.suffix.lower() in forbidden or f.stat().st_size > 25 * 1024**2 for f in files):
        raise ValueError('Forbidden or oversized deployment asset')
    if len(files) > 20000:
        raise ValueError('Cloudflare Pages asset count exceeded')
    print(json.dumps(dict(directory=str(args.output), files=len(files), verified_assets=len(inventory),
                          bytes=sum(f.stat().st_size for f in files))))


if __name__ == '__main__':
    main()
