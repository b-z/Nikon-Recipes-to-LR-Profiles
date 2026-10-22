"""Create local Release assets. Does not commit, push, create GitHub repositories or publish."""

import argparse
import json
import zipfile
from pathlib import Path

from nikon_recipes_lr import __version__
from nikon_recipes_lr.nx import sha256
from nikon_recipes_lr.profile import read_profile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profiles", required=True)
    p.add_argument("--metrics", required=True)
    p.add_argument("--samples")
    p.add_argument("--output", required=True)
    p.add_argument("--version", default=__version__)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rows = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    profiles = Path(args.profiles)
    if len(rows) != 236:
        raise ValueError("Nikon pack must contain all 236 conversions")
    ids = set()
    for row in rows:
        source = profiles / row["file"]
        lut, metadata = read_profile(source)
        if row["recipe"].startswith("Fuji_"):
            raise ValueError("Fuji simulation is outside the release scope")
        if sha256(source) != row["sha256"]:
            raise ValueError("Profile checksum mismatch")
        if metadata["uuid"] in ids:
            raise ValueError("Duplicate profile UUID")
        if metadata["table_id"] != row["source_table_id"]:
            raise ValueError("Published table changed from selected conversion")
        ids.add(metadata["uuid"])
    destination = out / f"nikon-recipes-lr-profiles-{args.version}.zip"
    if destination.exists():
        raise FileExistsError(destination)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for row in rows:
            archive.write(profiles / row["file"], "profiles/" + row["file"])
        archive.write(args.metrics, "manifest.json")
        for name in ("LICENSE", "PROFILE_LICENSE.md", "THIRD_PARTY_NOTICES.md"):
            archive.write(root / name, name)
        # One README for the archive, made from the install guides (English, Chinese, Japanese).
        guides = [
            (root / "docs" / lang / "INSTALL.md").read_text(encoding="utf-8").strip() for lang in ("en", "zh", "ja")
        ]
        archive.writestr("README.md", "\n\n---\n\n".join(guides) + "\n")
        archive.writestr("SHA256SUMS.profiles", "".join(f"{r['sha256']}  profiles/{r['file']}\n" for r in rows))
    artifacts = [destination]
    if args.samples:
        directory = Path(args.samples)
        manifest = json.loads((root / "samples/manifest.json").read_text(encoding="utf-8"))
        destination = out / f"nikon-recipes-lr-samples-{args.version}.zip"
        if destination.exists():
            raise FileExistsError(destination)
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_STORED) as archive:
            for row in manifest:
                path = directory / row["file"]
                if sha256(path) != row["sha256"]:
                    raise ValueError("Sample checksum mismatch")
                archive.write(path, row["file"])
            archive.write(root / "samples/manifest.json", "manifest.json")
            archive.write(root / "samples/LICENSE.md", "LICENSE.md")
            archive.write(root / "samples/README.md", "README.md")
        artifacts.append(destination)
    with (out / "SHA256SUMS").open("w", encoding="utf-8") as stream:
        for path in artifacts:
            stream.write(f"{sha256(path)}  {path.name}\n")
    print(json.dumps([dict(file=str(p), bytes=p.stat().st_size, sha256=sha256(p)) for p in artifacts], indent=2))


if __name__ == "__main__":
    main()
