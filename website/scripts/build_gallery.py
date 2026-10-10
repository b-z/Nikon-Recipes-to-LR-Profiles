"""Generate documented numerical previews from baseline NPZs and a profile pack.

Input per photo: <id>_base.npz (overview, encoded Adobe RGB float32), optional
<id>_actual_Base.npz (crop, uint16 Adobe RGB), plus adobe_rgb.icc. No RAW rendering
or profile installation is performed. Derived photos retain the sample license.
"""
import argparse
import html
import io
import json
import shutil
from urllib.parse import quote
from pathlib import Path
import numpy as np
from PIL import Image,ImageCms


def cached_input(rgb,n):
    from nikon_recipes_lr.tetrahedral import vertices
    corners,weights=vertices(rgb,n)
    indices=((corners[...,0]*n+corners[...,1])*n+corners[...,2]).astype('i4')
    return indices,weights.astype('f4'),rgb.shape


def evaluate(lut,cache):
    indices,weights,shape=cache
    table=lut.reshape(-1,3).astype('f4');out=np.empty((len(indices),3),dtype='f4')
    for start in range(0,len(indices),65536):
        ids=indices[start:start+65536];w=weights[start:start+65536]
        out[start:start+65536]=np.sum(table[ids]*w[...,None],axis=1)
    return out.reshape(shape)


def main():
    from nikon_recipes_lr.profile import read_profile
    from gallery_assets import asset_location, inventory
    root=Path(__file__).resolve().parents[2]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profiles',required=True);p.add_argument('--baselines',required=True)
    p.add_argument('--metrics',required=True);p.add_argument('--assets',required=True)
    args=p.parse_args();profiles=Path(args.profiles);baselines=Path(args.baselines);docs=root/'docs'
    assets=Path(args.assets);data=root/'website/data'
    asset_location(assets,root)
    dest=assets/'images';dest.mkdir(exist_ok=True,parents=True)
    rows=json.loads(Path(args.metrics).read_text(encoding='utf-8'))
    adobe=ImageCms.ImageCmsProfile(io.BytesIO((baselines/'adobe_rgb.icc').read_bytes()))
    srgb=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB'));srgbbytes=srgb.tobytes()
    conversion=ImageCms.buildTransformFromOpenProfiles(adobe,srgb,'RGB','RGB')
    def display(array,path,crop=False):
        pic=Image.fromarray(np.rint(np.clip(array,0,1)*255).astype('u1'))
        pic=ImageCms.applyTransform(pic,conversion)
        if not crop:pic.thumbnail((1024,1024),Image.Resampling.LANCZOS)
        if crop:pic.save(path,lossless=True,method=4,icc_profile=srgbbytes)
        else:pic.save(path,quality=86,icc_profile=srgbbytes)
    manifest=[]
    for stem in ('9046','2849','2694','5054'):
        baseline=np.load(baselines/f'{stem}_base.npz')['overview'];overview_cache=cached_input(baseline,32)
        display(baseline,dest/f'{stem}_base.jpg')
        for i,row in enumerate(rows):
            file=dest/f'{stem}_{row["recipe"]}.jpg'
            lut,metadata=read_profile(profiles/row['file'])
            if len(lut)!=32:raise ValueError('Gallery expects the shipped 32³ tables')
            display(evaluate(lut,overview_cache),file)
            if (i+1)%40==0:print(stem,i+1,'/',len(rows),'previews',flush=True)
        manifest.append(dict(photo=f'_DSC{stem}.NEF',amount=1.,type='Numerical tetrahedral preview on Camera Raw Adobe Standard baseline; not NX ground truth',
                             overview='16-bit area average, factor 6, before transform',crop=None))
        del overview_cache,baseline
        print(stem,'complete',flush=True)
    for path in baselines.glob('*_actual_*.jpg'):shutil.copyfile(path,dest/path.name)
    shutil.copyfile(baselines/'acr_validation.json',docs/'acr_validation.json')
    shutil.copyfile(baselines/'roi_manifest.json',data/'roi_manifest.json')
    (data/'gallery_manifest.json').write_text(json.dumps(manifest,indent=2), encoding='utf-8')
    # Sidebar previews are website assets too.
    thumbs=assets/'images/thumbs';thumbs.mkdir(exist_ok=True)
    for row in rows:
        with Image.open(dest/f'9046_{row["recipe"]}.jpg') as pic:
            pic.thumbnail((172,116),Image.Resampling.LANCZOS)
            pic.save(thumbs/f'{row["recipe"]}.jpg',quality=82,icc_profile=pic.info.get('icc_profile'))
    inventory(assets,data/'assets_manifest.json')
    (assets/'assets_manifest.json').write_text((data/'assets_manifest.json').read_text(encoding='utf-8'), encoding='utf-8')
    build_pages(rows,docs,include_previews=False)


def build_y8_pages(rows, docs):
    metrics = json.loads((Path(__file__).resolve().parents[1]/'data/y8_metrics.json').read_text(encoding='utf-8'))
    previous = {row['recipe']:row for row in rows}
    pages = docs/'recipes/y8'
    pages.mkdir(parents=True, exist_ok=True)
    for row in metrics:
        recipe=row['recipe']; old=previous[recipe]; fit=row['fit']; risk=row['banding']
        page=f"""# {html.escape(old['display'])} — Y8

Original recipe by {html.escape(old['author'])}. [Y8 method and review](../../Y8_REBUILD.md) · [Y7 measurements](../{quote(recipe,safe='')}.md).

| Measurement | Score |
|---|---:|
| Chart mean / median ΔE | {fit['mean']:.4f} / {fit['median']:.4f} |
| Chart p95 ΔE | {fit['p95']:.4f} |
| Valid chart samples | {fit['sample_count']} |
| Heldout mean ΔE | {fit['heldout']['mean']:.4f} |
| Native face jump p99 / maximum | {risk['face_jump_p99']:.4f} / {risk['face_jump_max']:.4f} |

Chart scores do not certify visible-band-free output. Group membership is the historical Y7 review. XMP: `{row['file']}`.
"""
        (pages/f'{recipe}.md').write_text(page, encoding='utf-8')


def build_pages(rows,docs,include_previews=True):
    references_path=docs/'nx_references.json'
    references=json.loads(references_path.read_text(encoding='utf-8')) if references_path.exists() else []
    nx_lookup={(r['photo'],r['recipe']):r for r in references}
    pages=docs/'recipes';pages.mkdir(exist_ok=True)
    index=['# Recipe catalog — 0.1.0','',
           '236 Nikon conversions. **Banding is a known issue**; scores are not universal visibility thresholds. [Definitions](en/metrics.md) · [Online gallery](https://nikon-recipes-to-lr-profiles.pages.dev/)', '',
           'Chart ΔE is current-table evaluation on existing targets. Face p99 measures native RGB slope change globally; it is not ΔE. All 236 profiles use the Y7 native tetrahedral fitter. Neutral warning icons mark the 58 recipes with residual banding in the 2026-10-10 owner review. Full four-scene comparisons are available in the online gallery.', '',
           '| Recipe / original author | Chart mean ΔE | Chart p95 | Face p99 | Face max | Source |',
           '|---|---:|---:|---:|---:|---|']
    for row in rows:
        recipe=row['recipe'];fit=row['fit'];risk=row['banding'];author=html.escape(row['author']);display=html.escape(row['display'])
        index.append(f'| [{display} — {author}](recipes/{recipe}.md) | {fit["mean"]:.3f} | {fit["p95"]:.3f} | {risk["face_jump_p99"]:.3f} | {risk["face_jump_max"]:.3f} | {row["source_version"]} |')
        page=f'''# {display}

Original author: **{author}**. [NP3 archive]({row['input_recipe_source']}) · [All recipes](../RECIPES.md)

Profile: `{row['file']}` · Source conversion: **{row['source_version']}** · Amount: **100%**.

| Measurement | Score |
|---|---:|
| Chart mean / median ΔE | {fit['mean']:.4f} / {fit['median']:.4f} |
| Chart p95 ΔE | {fit['p95']:.4f} |
| Valid chart samples | {fit['sample_count']} |
| Native face jump p99 / maximum | {risk['face_jump_p99']:.4f} / {risk['face_jump_max']:.4f} |
| Native face jump RMS | {risk['face_jump_rms']:.4f} |
| Audited faces | {risk['face_count']} |

Review: **{row['owner_review']}**. NX target: {row['measurement_policy']}.

[Score definitions and limitations](../en/metrics.md). These are current-table chart scores and global structural banding-risk scores, not a visible-band pass/fail verdict. A low average ΔE does not guarantee smooth skies or bokeh.

## Comparison previews

Right: numerical tetrahedral Lightroom table preview, 100% Amount. Left: owner-exported NX Studio reference where available; otherwise Adobe Standard, explicitly labeled. Display previews are 8-bit sRGB; use the RAW samples for final Lightroom evaluation. [Compact NX comparison sheets](../comparisons/README.md).

'''
        if not include_previews:
            page=page.split('## Comparison previews')[0]+f'## Visual comparisons\n\n[View this recipe on all four scenes](https://nikon-recipes-to-lr-profiles.pages.dev/docs/gallery#{quote(recipe,safe="")}). [Small NX/LR contact sheets](../comparisons/README.md).\n\n'
        scenes=[('9046','Landscape test 1'),('2849','Landscape test 2'),('2694','Banding test 1'),('5054','Banding test 2')]
        for stem,label in (scenes if include_previews else []):
            nx=nx_lookup.get((stem,recipe))
            before=nx['path'] if nx else f'images/{stem}_base.jpg'
            caption='NX Studio' if nx else 'Adobe Standard (NX reference pending)'
            page+=f'### {label}\n\n![{caption}](../{before})\n\n![Converted {display}](../images/{stem}_{recipe}.jpg)\n\n'
        verified_photos=[v['photo'] for v in json.loads((docs/'acr_validation.json').read_text(encoding='utf-8')) if v['recipe']==recipe]
        if verified_photos:
            page+='## Actual Camera Raw verification\n\nThese are actual Camera Raw exports, separate from the numerical previews. [Measured preview/render differences](../acr_validation.json).\n\n'
            for stem in (verified_photos if include_previews else []):page+=f'![Actual Camera Raw _DSC{stem}](../images/{stem}_actual_{recipe}.jpg)\n\n'
        page+='Photos © b-z / Zhou Bowei. [Project test/comparison permission only](../../samples/LICENSE.md); other uses require permission.\n'
        (pages/f'{recipe}.md').write_text(page, encoding='utf-8')
    (docs/'RECIPES.md').write_text('\n'.join(index)+'\n', encoding='utf-8')
    if not include_previews:
        return
    build_y8_pages(rows,docs)
    data=json.dumps(rows,ensure_ascii=False).replace('</','<\\/')
    page=(Path(__file__).resolve().parents[1].joinpath('gallery.template.html').read_text(encoding='utf-8')
          .replace('__DATA__',data)
          .replace('__BANDING_WARNINGS__',(Path(__file__).resolve().parents[1]/'data/banding_warnings.json').read_text(encoding='utf-8'))
          .replace('__Y8_METRICS__',(Path(__file__).resolve().parents[1]/'data/y8_metrics.json').read_text(encoding='utf-8'))
          .replace('__DOWNLOADS__',(Path(__file__).resolve().parents[1]/'data/downloads.json').read_text(encoding='utf-8'))
          .replace('__REFERENCES__',json.dumps(references).replace('</','<\\/')))
    (docs/'gallery.html').write_text(page, encoding='utf-8')


if __name__=='__main__':main()
