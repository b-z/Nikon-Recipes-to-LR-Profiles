"""Build the static gallery website from the template, the release manifests and an external image library.

Output layout (deploy the whole directory, e.g. with Cloudflare Pages Direct Upload):
  index.html, payment.js, _redirects, _headers
  images/{nx,y9,y8}/<scene>_<recipe>.jpg   NX Studio, release 1.0 and release 0.2 previews
  images/{adobe,flex}/<scene>.jpg          base profiles without a recipe
  images/thumbs/<recipe>.jpg               list thumbnails
  profiles/<camera>/*.xmp                  per-recipe downloads, identical to the files in the release packs

Every profile is checked against its release manifest, and every preview the page links to must exist.
Images are made by make_previews.py.
"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from nikon_recipes_lr import __version__
from nikon_recipes_lr.cameras import ADOBE, FLEX_CAMERAS, adobe_profile, camera_profile

ROOT = Path(__file__).resolve().parents[2]
SCENES = ("9046", "2849", "2694", "5054")
IMAGE_DIRS = ("nx", "y9", "y8", "adobe", "flex", "thumbs")
FORBIDDEN = {".nef", ".np3", ".ncp", ".nksc", ".tif", ".tiff", ".toml", ".env"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_profiles(rows, source):
    texts = {}
    for row in rows:
        path = source / row["file"]
        if not path.is_file() or sha256(path) != row["sha256"]:
            raise ValueError(f"Missing or changed profile: {path}")
        texts[row["recipe"]] = (row["file"], path.read_text(encoding="utf-8"))
    return texts


def write_packs(out, current, previous):
    """Write the per-recipe downloads exactly as the release packs contain them."""
    for camera in FLEX_CAMERAS:
        folder = out / "profiles" / camera.slug
        folder.mkdir(parents=True)
        for recipe, (name, text) in current.items():
            (folder / name).write_text(camera_profile(text, recipe, camera), encoding="utf-8")
    folder = out / "profiles" / ADOBE.slug
    folder.mkdir(parents=True)
    for recipe, (name, text) in previous.items():
        (folder / name).write_text(adobe_profile(text, recipe), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--images", type=Path, required=True, help="Image library made by make_previews.py")
    p.add_argument(
        "--profiles", type=Path, required=True, help="Reference (Nikon Z 8) profiles, e.g. profiles/ of the z8 pack"
    )
    p.add_argument("--previous-profiles", type=Path, required=True, help="profiles/ folder of the 0.2.0 release ZIP")
    p.add_argument("--output", type=Path, default=ROOT / "website/dist")
    args = p.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        p.error("Output must be empty; use a new build directory")
    data = ROOT / "website/data"
    current = json.loads((ROOT / "docs/release_manifest.json").read_text(encoding="utf-8"))
    previous = json.loads((data / "release_0.2.0_manifest.json").read_text(encoding="utf-8"))
    downloads = json.loads((data / "downloads.json").read_text(encoding="utf-8"))
    references = json.loads((data / "nx_references.json").read_text(encoding="utf-8"))
    recipes = [row["recipe"] for row in current]
    if [row["recipe"] for row in previous] != recipes or [row["recipe"] for row in downloads] != recipes:
        raise ValueError("Release manifests and downloads list different recipes")

    needed = [f"{d}/{s}_{r}.jpg" for d in ("y9", "y8") for s in SCENES for r in recipes]
    needed += [f"{d}/{s}.jpg" for d in ("adobe", "flex") for s in SCENES]
    needed += [f"thumbs/{r}.jpg" for r in recipes]
    needed += [ref["path"].removeprefix("images/") for ref in references]
    missing = [n for n in needed if not (args.images / n).is_file()]
    if missing:
        raise ValueError(f"{len(missing)} images missing, e.g. {missing[:3]}")

    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    for name in sorted(set(needed)):
        target = out / "images" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.images / name, target)
    write_packs(out, read_profiles(current, args.profiles), read_profiles(previous, args.previous_profiles))
    cameras = [dict(slug=c.slug, label=c.label, flex=True) for c in FLEX_CAMERAS]
    cameras.append(dict(slug=ADOBE.slug, label=ADOBE.label, flex=False))

    def js(value):
        return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")

    page = (
        (ROOT / "website/gallery.template.html")
        .read_text(encoding="utf-8")
        .replace("__DATA__", js(current))
        .replace("__PREVIOUS__", js(previous))
        .replace("__REFERENCES__", js(references))
        .replace("__DOWNLOADS__", js(downloads))
        .replace("__CAMERAS__", js(cameras))
        .replace("__VERSION__", __version__)
    )
    if any(
        token in page
        for token in ("__DATA__", "__PREVIOUS__", "__REFERENCES__", "__DOWNLOADS__", "__CAMERAS__", "__VERSION__")
    ):
        raise ValueError("Unreplaced placeholder in the template")
    (out / "index.html").write_text(page, encoding="utf-8")
    shutil.copyfile(ROOT / "website/payment.js", out / "payment.js")
    # Addresses of the earlier gallery keep working.
    (out / "_redirects").write_text(
        "/docs/gallery.html / 301\n/docs/gallery / 301\n/gallery / 301\n/docs/* / 301\n", encoding="utf-8"
    )
    (out / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
        "/profiles/*\n  Content-Type: application/octet-stream\n  Content-Disposition: attachment\n",
        encoding="utf-8",
    )
    files = [f for f in out.rglob("*") if f.is_file()]
    if any(f.suffix.lower() in FORBIDDEN or f.stat().st_size > 25 * 1024**2 for f in files):
        raise ValueError("Forbidden or oversized file in the build")
    if len(files) > 20000:
        raise ValueError("Cloudflare Pages file limit exceeded")
    print(json.dumps(dict(output=str(out), files=len(files), bytes=sum(f.stat().st_size for f in files)), indent=2))


if __name__ == "__main__":
    main()
