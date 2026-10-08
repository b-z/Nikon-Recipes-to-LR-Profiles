"""Import owner-produced NX JPEG references and make compact NX/LR contact sheets.

Only the manifest's named exports are read. No source image is modified. Public
derivatives contain sRGB ICC and no EXIF. Missing references are never fabricated.
"""
import argparse
import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageCms, ImageDraw, ImageFont, ImageOps
from build_gallery import build_pages
from gallery_assets import asset_location, compact_sheets, inventory

SCENES = [('9046', 'Landscape test 1'), ('2849', 'Landscape test 2'),
          ('2694', 'Banding test 1'), ('5054', 'Banding test 2')]


def srgb_image(path):
    with Image.open(path) as image:
        dimensions = image.size
        if image.getexif().get(274) in (5, 6, 7, 8):
            dimensions = dimensions[::-1]
        # Decode a bounded-size JPEG for web previews, rather than several
        # full-resolution 45 MP buffers. These derivatives are not fit inputs.
        image.draft('RGB', (768, 768))
        image.load()
        rgb = ImageOps.exif_transpose(image).convert('RGB')
        icc = image.info.get('icc_profile')
        if not icc:
            raise ValueError(f'Export has no ICC profile: {path}')
        result = ImageCms.profileToProfile(rgb, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                          ImageCms.createProfile('sRGB'), outputMode='RGB')
        result.info.clear()
        result.info['source_dimensions'] = dimensions
        return result


def sheets(rows, refs, docs, per_sheet=8):
    destination = docs / 'comparisons'
    destination.mkdir(exist_ok=True)
    # Remove only previously generated sheets, keeping unrelated files intact.
    previous = destination / 'manifest.json'
    if previous.exists():
        for entry in json.loads(previous.read_text(encoding='utf-8')):
            name = Path(entry['path']).name
            if name.endswith('.jpg'):
                (destination / name).unlink(missing_ok=True)
    lookup = {(r['photo'], r['recipe']): r for r in refs}
    ready = sorted((r for r in rows if all((stem,r['recipe']) in lookup for stem,_ in SCENES)),
                   key=lambda r:(r['fit']['mean'],r['recipe']))
    names = {}
    for row in rows:
        names[row['display']] = names.get(row['display'],0)+1
    def font(size):
        for name in ('DejaVuSans.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf'):
            try:
                return ImageFont.truetype(name,size)
            except OSError:
                pass
        return ImageFont.load_default(size=size)
    title_font = font(30)
    metric_font = font(22)
    label_font = font(16)
    header_font = font(19)
    tile_w,tile_h,gap,margin,row_h = 240,160,8,24,212
    width=margin*2+tile_w*8+gap*7
    profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    result=[]
    for start in range(0,len(ready),per_sheet):
        subset=ready[start:start+per_sheet]
        canvas=Image.new('RGB',(width,68+len(subset)*row_h),'#202426');draw=ImageDraw.Draw(canvas)
        draw.text((margin,12),'NX Studio / Our LR conversion · recipes ordered by ΔE',font=header_font,fill='white')
        draw.text((margin,39),'Landscape 1 / Landscape 2 / Banding 1 / Banding 2 · each pair: NX, LR',font=label_font,fill='#cbd2d6')
        for i,row in enumerate(subset):
            y=68+i*row_h
            name=row['display']+((' ['+row['recipe']+']') if names[row['display']]>1 else '')
            draw.text((margin,y),name,font=title_font,fill='white')
            name_width=draw.textlength(name,font=title_font)
            metrics=f"ΔE {row['fit']['mean']:.3f} · Banding risk {row['banding']['face_jump_p99']:.3f}"
            draw.text((margin+name_width+24,y+6),metrics,font=metric_font,fill='#cbd2d6')
            for scene_index,(stem,_) in enumerate(SCENES):
                paths=[docs/lookup[stem,row['recipe']]['path'],docs/'images'/f"{stem}_{row['recipe']}.jpg"]
                for side,(path,label) in enumerate(zip(paths,('NX','LR'))):
                    x=margin+(scene_index*2+side)*(tile_w+gap)
                    with Image.open(path) as pic:
                        tile=ImageOps.contain(pic.convert('RGB'),(tile_w,tile_h),Image.Resampling.LANCZOS)
                        canvas.paste(tile,(x+(tile_w-tile.width)//2,y+40+(tile_h-tile.height)//2))
                    badge=Image.new('RGBA',(tile_w,tile_h),(0,0,0,0));b=ImageDraw.Draw(badge)
                    label_width=b.textlength(label,font=label_font)
                    b.rounded_rectangle((5,5,15+label_width,31),radius=3,fill=(0,0,0,165))
                    b.text((10,8),label,font=label_font,fill='white')
                    canvas.paste(badge,(x,y+40),badge)
        name=f'recipes_{start//per_sheet+1:02}.jpg'
        canvas.save(destination/name,quality=95,subsampling=0,icc_profile=profile)
        result.append(dict(path='comparisons/'+name,recipes=[r['recipe'] for r in subset],
                           mean_delta_e=[r['fit']['mean'] for r in subset],scene_order=[stem for stem,_ in SCENES],
                           rows=len(subset),images_per_row=8,width=width))
    (destination/'manifest.json').write_text(json.dumps(result,indent=2), encoding='utf-8')
    text=['# NX Studio / Lightroom comparison sheets','',
          'Recipes are ordered by ascending chart mean ΔE. Each sheet has up to eight recipe rows; each row shows all four scenes as NX/LR pairs (eight photographs). Names, ΔE and Banding risk are above each row. NX and LR labels overlay the photographs. These are high-quality sRGB visual previews, not precision banding measurements.','',
          'Photos © b-z / Zhou Bowei. [Project comparison permission](../../samples/LICENSE.md).','']
    for entry in result:
        text.extend([f"## Recipes {Path(entry['path']).stem.split('_')[-1]}",'',f"![NX / LR on four scenes]({Path(entry['path']).name})",''])
    (destination/'README.md').write_text('\n'.join(text)+'\n', encoding='utf-8')
    return len(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, required=True)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument('--docs', type=Path, default=root / 'docs')
    parser.add_argument('--assets', type=Path, required=True)
    args = parser.parse_args()
    asset_location(args.assets, root)
    rows = json.loads((args.docs / 'recipe_metrics.json').read_text(encoding='utf-8'))
    batch = json.loads((args.batch / 'manifest.json').read_text(encoding='utf-8'))
    target = args.assets / 'images/nx'; target.mkdir(parents=True, exist_ok=True)
    previous = root / 'website/data/nx_references.json'
    refs = {(r['photo'], r['recipe']): r for r in json.loads(previous.read_text(encoding='utf-8'))} if previous.exists() else {}
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    export_lists = {}
    for folder in {item['folder'] for item in batch}:
        group = args.batch / folder
        # NX can save alongside the RAWs or in an exports subdirectory.
        export_lists[folder] = list(group.iterdir())
        if (group / 'exports').is_dir():
            export_lists[folder] += list((group / 'exports').iterdir())
    jobs = []
    for item in batch:
        candidates = [p for p in export_lists[item['folder']] if p.stem == Path(item['jpeg']).stem and p.suffix.lower() in ('.jpg', '.jpeg')]
        if len(candidates) > 1:
            raise ValueError('Ambiguous JPEG: ' + item['jpeg'])
        if not candidates:
            continue
        jobs.append((item, candidates[0]))

    def import_one(job):
        item, path = job
        pic = srgb_image(path)
        # Keep original dimensions in metadata. Only derived previews are resized.
        dimensions = pic.info['source_dimensions']
        pic.thumbnail((768, 768), Image.Resampling.LANCZOS)
        name = f'{item["photo"]}_{item["recipe"]}.jpg'
        pic.save(target / name, quality=90, icc_profile=profile)
        pic.close()
        return dict(photo=item['photo'], recipe=item['recipe'],
            path='images/nx/' + name, source_dimensions=dimensions,
            source='Owner export from NX Studio, original recipe color/tonal settings; detail processing disabled')
    imported = 0
    # Two bounded JPEG decoders overlap NAS reads without loading a batch into RAM.
    with ThreadPoolExecutor(max_workers=2) as pool:
        for reference in pool.map(import_one, jobs):
            refs[reference['photo'], reference['recipe']] = reference
            imported += 1
            if imported % 40 == 0:
                print(f'Imported {imported} NX references', flush=True)
    reference_rows = list(refs.values())
    previous.write_text(json.dumps(reference_rows, indent=2), encoding='utf-8')
    count = sheets(rows, reference_rows, args.assets)
    compact_sheets(args.assets, args.docs)
    manifest = root / 'website/data/assets_manifest.json'
    inventory(args.assets, manifest)
    (args.assets/'assets_manifest.json').write_text(manifest.read_text(encoding='utf-8'), encoding='utf-8')
    build_pages(rows, args.docs, include_previews=False)
    print(json.dumps(dict(imported=imported, references=len(refs), contact_sheets=count)))


if __name__ == '__main__':
    main()
