"""Fit release profiles for many recipes at once, the way the published releases are made.

Input: NX Studio 16-bit TIFF exports of a calibration kit's chart, one per recipe, named <recipe>.TIF (the
names `prepare-nx` gives the NEFs). The kit is calibration/z8 unless --camera names another body with a kit;
the training and test patches are always those of calibration/z8/splits.npz, since every kit uses the same
patches. For every recipe the script samples the TIFF, fits the smooth spline on the
kit's fixed training patches, scores it on the held-out patches, audits banding risk and writes a release
profile plus one manifest row.

  python scripts/build_release_profiles.py --nx /path/to/nx-batch --version 1.1.0 --output /path/to/out
  python scripts/build_release_profiles.py --camera zf --nx /path/to/zf-batch --version 1.1.0 --output /path/to/zf

For a body other than the Z 8, the profiles are the source of that body's color tables: `package_release.py`
puts each table into the reference profile of the recipe (see `nikon_recipes_lr.cameras`).

Recipe names, creators and creator groups come from docs/release_manifest.json; new recipes need an entry in
--recipes (a JSON list of {"recipe", "display", "author", "group"}). The Picture Control name for `sidecars`
is read from the NP3 when --np3 points at the NP3 archive.
"""

import argparse
import hashlib
import json
import re
import uuid
from pathlib import Path

import numpy as np

from nikon_recipes_lr.calibration import sample_tiff
from nikon_recipes_lr.cameras import FLEX_CAMERAS
from nikon_recipes_lr.color import de2000, lab
from nikon_recipes_lr.np3 import inspect
from nikon_recipes_lr.profile import build_profile, read_profile
from nikon_recipes_lr.spline import SplineFitter
from nikon_recipes_lr.tetrahedral import audit, lookup

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ROOT / "calibration/z8/splits.npz"
CAMERAS = {c.slug: c for c in FLEX_CAMERAS if c.fitted}
BASELINES = {"Camera Flexible Color": "camera-flexible-color.npy", "Adobe Standard": "adobe-standard.npy"}
NP3_SOURCE = "https://github.com/shouryan01/Nikon-Recipes"
URL = "https://github.com/b-z/Nikon-Recipes-to-LR-Profiles"


def clipped(a):
    return ((a > 0.999) | (a < 0.0005)).any(1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nx", type=Path, required=True, help="Folder of NX Studio TIFF exports named <recipe>.TIF")
    p.add_argument("--version", required=True, help="Release version, e.g. 1.1.0")
    p.add_argument("--output", type=Path, required=True, help="New folder for profiles/ and manifest.json")
    p.add_argument("--base", choices=sorted(BASELINES), default="Camera Flexible Color")
    p.add_argument("--recipes", type=Path, help="JSON with names and creators of recipes not yet released")
    p.add_argument("--np3", type=Path, help="NP3 archive, to record each recipe's Picture Control name")
    p.add_argument("--camera", choices=sorted(CAMERAS), default="z8", help="Body whose calibration kit was exported")
    p.add_argument("--lambda", dest="lam", type=float, default=0.001)
    args = p.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        p.error("Output must be a new or empty folder")
    (args.output / "profiles").mkdir(parents=True, exist_ok=True)
    series = ".".join(args.version.split(".")[:2])
    body = CAMERAS[args.camera]
    kit = ROOT / "calibration" / body.slug
    camera = body.restriction if args.base == "Camera Flexible Color" else ""
    known = {r["recipe"]: r for r in json.loads((ROOT / "docs/release_manifest.json").read_text(encoding="utf-8"))}
    if args.recipes:
        known.update({r["recipe"]: r for r in json.loads(args.recipes.read_text(encoding="utf-8"))})
    np3 = {}
    if args.np3:
        np3 = {f.stem.replace(" ", "_"): f for f in args.np3.rglob("*") if f.suffix.lower() == ".np3"}
    x = np.load(kit / BASELINES[args.base])
    split = dict(np.load(SPLITS))
    # prepare-nx names the NEFs after the NP3 files (recipe IDs with spaces), with runs of characters such as
    # " (" or "+" replaced by "_".
    by_file = {re.sub(r"[^\w.-]+", "_", r.replace("_", " ")): r for r in known}
    by_file.update({re.sub(r"[^\w.-]+", "_", r): r for r in known})
    tifs = sorted(f for f in args.nx.iterdir() if f.suffix.lower() in (".tif", ".tiff"))
    unknown = [f.name for f in tifs if by_file.get(f.stem, f.stem) not in known]
    if unknown:
        raise SystemExit(f"No name or creator for {', '.join(unknown)}; add them to --recipes")
    rows = []
    for tif in tifs:
        recipe = by_file.get(tif.stem, tif.stem)
        meta = known[recipe]
        y = np.array([s["measured"] for s in sample_tiff(tif, kit / "chart.json")])
        ok = ~(clipped(x) | clipped(y))
        lut, _, _ = SplineFitter(x[split["train"] & ok], 16).fit(y[split["train"] & ok], args.lam)
        d = de2000(lab(lookup(lut, x[ok])), lab(y[ok]))
        held = split["test"] & ok
        dh = de2000(lab(lookup(lut, x[held])), lab(y[held]))
        risk = audit(lut)["all_face_jump"]
        name = f"{meta['display']} by {meta['author']} [NRLR {series}]"
        text = build_profile(
            lut,
            name,
            meta["author"],
            group=f"Nikon Recipes LR {series}/{meta['group']}",
            camera=camera,
            base=args.base,
            profile_uuid=uuid.uuid5(
                uuid.NAMESPACE_URL, f"nikon-recipes-to-lr-profiles:{args.version}:{body.slug}:{recipe}"
            ).hex.upper(),
            short_name=f"{meta['display']} [NRLR {series}]",
            description=f'Original Imaging Recipe "{meta["display"]}" by {meta["author"]}. Converted to a Lightroom / '
            f"Camera Raw profile (RGB table on {args.base}{', ' + body.label if camera else ''}) by Nikon Recipes to LR "
            f"Profiles: {URL}. Use the Amount slider for strength. Color and tone only.",
        )
        out = args.output / "profiles" / f"NikonRecipes_{recipe}.xmp"
        out.write_text(text, encoding="utf-8")
        _, info = read_profile(out)
        rows.append(
            dict(
                recipe=recipe,
                display=meta["display"],
                author=meta["author"],
                group=meta["group"],
                picture_control=inspect(np3[recipe])["name"] if recipe in np3 else meta.get("picture_control"),
                file=out.name,
                uuid=info["uuid"],
                sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                source_table_id=info["table_id"],
                base=args.base,
                camera=camera,
                kit=body.slug,
                fit=dict(
                    mean=float(d.mean()),
                    median=float(np.median(d)),
                    p95=float(np.percentile(d, 95)),
                    sample_count=int(ok.sum()),
                    heldout=dict(count=int(held.sum()), mean=float(dh.mean()), p95=float(np.percentile(dh, 95))),
                ),
                banding=dict(face_jump_p99=risk["p99"], face_jump_max=risk["max"], face_jump_rms=risk["rms"]),
                input_recipe_source=meta.get("input_recipe_source", NP3_SOURCE),
            )
        )
        print(
            f"{recipe}: chart ΔE {d.mean():.3f}, held-out {dh.mean():.3f}, banding risk {risk['p99']:.3f}", flush=True
        )
    (args.output / "manifest.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(rows)} profiles in {args.output}")


if __name__ == "__main__":
    main()
