"""Build a static gallery from external assets; never write images into docs/."""

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

from build_gallery import write_gallery_html
from gallery_assets import asset_location


def main():
    root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--assets", type=Path, default=os.environ.get("NIKON_LR_WEBSITE_ASSETS"))
    p.add_argument("--output", type=Path, default=root / "website/dist")
    args = p.parse_args()
    if not args.assets or not args.assets.is_dir():
        p.error("Supply --assets or NIKON_LR_WEBSITE_ASSETS: an extracted website asset pack")
    asset_location(args.assets, root)
    if args.output.resolve().is_relative_to(root) and not args.output.resolve().is_relative_to(root / "website/dist"):
        p.error("In-checkout output must be under ignored website/dist/")
    if args.output.exists() and any(args.output.iterdir()):
        p.error("Output must be empty; use a new build directory")
    if args.output.resolve() == args.assets.resolve():
        p.error("Output must differ from assets")
    docs = root / "docs"
    data = root / "website/data"
    inventory = json.loads((data / "assets_manifest.json").read_text(encoding="utf-8"))
    rows = json.loads((data / "y7_metrics.json").read_text(encoding="utf-8"))
    y8_rows = json.loads((data / "y8_metrics.json").read_text(encoding="utf-8"))
    allowed_profiles = {row["file"] for row in rows + y8_rows}
    args.output.mkdir(parents=True, exist_ok=True)
    # Documentation stays light in Git; the site receives full-size assets below.
    paths = [f for f in docs.rglob("*") if f.is_file() and f.suffix in (".md", ".json", ".jpg")]
    paths += [root / name for name in ("LICENSE", "PROFILE_LICENSE.md", "THIRD_PARTY_NOTICES.md", "samples/LICENSE.md")]
    for source in paths:
        destination = args.output / source.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    for source in data.glob("*.json"):
        shutil.copyfile(source, args.output / "docs" / source.name)
        alias = args.output / "website/data" / source.name
        alias.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, alias)
    shutil.copyfile(root / "website/README.md", args.output / "website/README.md")
    # Stream each asset once, verifying hashes while copying. Fail on stale packs.
    for row in inventory:
        relative = Path(row["path"])
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or relative.parts[0] not in ("images", "comparisons", "profiles")
        ):
            raise ValueError("Unsafe asset path")
        if relative.suffix not in ((".xmp",) if relative.parts[0] == "profiles" else (".jpg", ".json", ".md")):
            raise ValueError("Unexpected asset type")
        if relative.parts[0] == "profiles" and (len(relative.parts) != 2 or relative.name not in allowed_profiles):
            raise ValueError("Unrecognized downloadable profile")
        source = args.assets / relative
        if not source.resolve().is_relative_to(args.assets.resolve()):
            raise ValueError("Asset leaves its directory")
        destination = args.output / "docs" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256()
        with source.open("rb") as inp, destination.open("wb") as out:
            for block in iter(lambda: inp.read(1024**2), b""):
                h.update(block)
                out.write(block)
        if h.hexdigest() != row["sha256"] or destination.stat().st_size != row["bytes"]:
            raise ValueError("Asset checksum mismatch: " + row["path"])
    rows = json.loads((data / "y7_metrics.json").read_text(encoding="utf-8"))
    refs = json.loads((data / "nx_references.json").read_text(encoding="utf-8"))
    for row in rows:
        profile = args.output / "docs/profiles" / row["file"]
        if not profile.is_file() or hashlib.sha256(profile.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("Missing or mismatched downloadable profile")
        for stem in ("9046", "2849", "2694", "5054"):
            if not (args.output / "docs/images" / f"{stem}_{row['recipe']}.jpg").is_file():
                raise ValueError("Missing conversion preview")
        if not (args.output / "docs/images/thumbs" / f"{row['recipe']}.jpg").is_file():
            raise ValueError("Missing recipe thumbnail")
    for row in y8_rows:
        profile = args.output / "docs/profiles" / row["file"]
        if not profile.is_file() or hashlib.sha256(profile.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("Missing or mismatched Y8 profile")
        for stem in ("9046", "2849", "2694", "5054"):
            if not (args.output / "docs/images/y8" / f"{stem}_{row['recipe']}.jpg").is_file():
                raise ValueError("Missing Y8 conversion preview")
        if not (args.output / "docs/images/y8/thumbs" / f"{row['recipe']}.jpg").is_file():
            raise ValueError("Missing Y8 thumbnail")
    for ref in refs:
        if not (args.output / "docs" / ref["path"]).is_file():
            raise ValueError("Missing NX reference")
    write_gallery_html(rows, args.output / "docs")
    (args.output / "_redirects").write_text(
        "/ /docs/gallery.html 302\n/gallery /docs/gallery.html 302\n"
        # Former per-version Y8 score pages; the catalog page now covers both versions.
        "/docs/recipes/y8/* /docs/recipes/:splat 301\n",
        encoding="utf-8",
    )
    (args.output / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/docs/profiles/*\n  Content-Type: application/octet-stream\n  Content-Disposition: attachment\n",
        encoding="utf-8",
    )
    files = [f for f in args.output.rglob("*") if f.is_file()]
    forbidden = {".nef", ".np3", ".ncp", ".nksc", ".tif", ".tiff", ".toml", ".env"}
    if any(f.suffix.lower() in forbidden or f.stat().st_size > 25 * 1024**2 for f in files):
        raise ValueError("Forbidden or oversized deployment asset")
    if len(files) > 20000:
        raise ValueError("Cloudflare Pages asset count exceeded")
    print(
        json.dumps(
            dict(
                directory=str(args.output),
                files=len(files),
                verified_assets=len(inventory),
                bytes=sum(f.stat().st_size for f in files),
            )
        )
    )


if __name__ == "__main__":
    main()
