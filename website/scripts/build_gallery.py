"""Generate documented numerical previews from baseline NPZs and a profile pack.

Input per photo: <id>_base.npz (overview, encoded Adobe RGB float32), optional
<id>_actual_Base.npz (crop, uint16 Adobe RGB), plus adobe_rgb.icc. No RAW rendering
or profile installation is performed. Derived photos retain the sample license.
"""

import argparse
import io
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms


def cached_input(rgb, n):
    from nikon_recipes_lr.tetrahedral import vertices

    corners, weights = vertices(rgb, n)
    indices = ((corners[..., 0] * n + corners[..., 1]) * n + corners[..., 2]).astype("i4")
    return indices, weights.astype("f4"), rgb.shape


def evaluate(lut, cache):
    indices, weights, shape = cache
    table = lut.reshape(-1, 3).astype("f4")
    out = np.empty((len(indices), 3), dtype="f4")
    for start in range(0, len(indices), 65536):
        ids = indices[start : start + 65536]
        w = weights[start : start + 65536]
        out[start : start + 65536] = np.sum(table[ids] * w[..., None], axis=1)
    return out.reshape(shape)


def main():
    from gallery_assets import asset_location, inventory

    from nikon_recipes_lr.profile import read_profile

    root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profiles", required=True)
    p.add_argument("--baselines", required=True)
    p.add_argument("--metrics", required=True)
    p.add_argument("--assets", required=True)
    args = p.parse_args()
    profiles = Path(args.profiles)
    baselines = Path(args.baselines)
    docs = root / "docs"
    assets = Path(args.assets)
    data = root / "website/data"
    asset_location(assets, root)
    dest = assets / "images"
    dest.mkdir(exist_ok=True, parents=True)
    rows = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    adobe = ImageCms.ImageCmsProfile(io.BytesIO((baselines / "adobe_rgb.icc").read_bytes()))
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
    srgbbytes = srgb.tobytes()
    conversion = ImageCms.buildTransformFromOpenProfiles(adobe, srgb, "RGB", "RGB")

    def display(array, path, crop=False):
        pic = Image.fromarray(np.rint(np.clip(array, 0, 1) * 255).astype("u1"))
        pic = ImageCms.applyTransform(pic, conversion)
        if not crop:
            pic.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        if crop:
            pic.save(path, lossless=True, method=4, icc_profile=srgbbytes)
        else:
            pic.save(path, quality=86, icc_profile=srgbbytes)

    manifest = []
    for stem in ("9046", "2849", "2694", "5054"):
        baseline = np.load(baselines / f"{stem}_base.npz")["overview"]
        overview_cache = cached_input(baseline, 32)
        display(baseline, dest / f"{stem}_base.jpg")
        for i, row in enumerate(rows):
            file = dest / f"{stem}_{row['recipe']}.jpg"
            lut, metadata = read_profile(profiles / row["file"])
            if len(lut) != 32:
                raise ValueError("Gallery expects the shipped 32³ tables")
            display(evaluate(lut, overview_cache), file)
            if (i + 1) % 40 == 0:
                print(stem, i + 1, "/", len(rows), "previews", flush=True)
        manifest.append(
            dict(
                photo=f"_DSC{stem}.NEF",
                amount=1.0,
                type="Numerical tetrahedral preview on Camera Raw Adobe Standard baseline; not NX ground truth",
                overview="16-bit area average, factor 6, before transform",
                crop=None,
            )
        )
        del overview_cache, baseline
        print(stem, "complete", flush=True)
    for path in baselines.glob("*_actual_*.jpg"):
        shutil.copyfile(path, dest / path.name)
    shutil.copyfile(baselines / "acr_validation.json", docs / "acr_validation.json")
    shutil.copyfile(baselines / "roi_manifest.json", data / "roi_manifest.json")
    (data / "gallery_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Sidebar previews are website assets too.
    thumbs = assets / "images/thumbs"
    thumbs.mkdir(exist_ok=True)
    for row in rows:
        with Image.open(dest / f"9046_{row['recipe']}.jpg") as pic:
            pic.thumbnail((172, 116), Image.Resampling.LANCZOS)
            pic.save(thumbs / f"{row['recipe']}.jpg", quality=82, icc_profile=pic.info.get("icc_profile"))
    inventory(assets, data / "assets_manifest.json")
    (assets / "assets_manifest.json").write_text(
        (data / "assets_manifest.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    # docs/RECIPES.md and docs/recipes/ describe the Release profiles; regenerate them with scripts/write_catalog.py.


def write_gallery_html(rows, docs):
    """Write docs/gallery.html from the template and the gallery data files.

    ``rows`` are the Y7 gallery rows (website/data/y7_metrics.json); Y8 rows,
    downloads and NX references are read from website/data/. The recipe catalog
    is not written here: it follows the Release (scripts/write_catalog.py).
    """
    site = Path(__file__).resolve().parents[1]
    references = json.loads((site / "data/nx_references.json").read_text(encoding="utf-8"))
    data = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    page = (
        (site / "gallery.template.html")
        .read_text(encoding="utf-8")
        .replace("__DATA__", data)
        .replace("__Y8_METRICS__", (site / "data/y8_metrics.json").read_text(encoding="utf-8"))
        .replace("__DOWNLOADS__", (site / "data/downloads.json").read_text(encoding="utf-8"))
        .replace("__REFERENCES__", json.dumps(references).replace("</", "<\\/"))
    )
    (docs / "gallery.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
