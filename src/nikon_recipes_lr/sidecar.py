"""Write XMP sidecars that apply the profile matching the Picture Control recorded in each Nikon RAW.

The camera stores the name of the active Picture Control (for an Imaging Recipe, the recipe's NP3 name)
in the NEF maker notes. Lightroom Classic and Camera Raw read a ``<name>.xmp`` sidecar next to the RAW,
so writing one before import makes the matching profile the photo's starting point.
"""

import json
import subprocess
from importlib.resources import files
from pathlib import Path

from .profile import import_sidecar, read_profile

RAW_SUFFIXES = {".nef", ".nrw"}
RELEASE_PREFIX = "NikonRecipes_"


def release_picture_controls():
    """Recipe ID (release file name without prefix) -> Picture Control name stored in its NP3."""
    return json.loads(files(__package__).joinpath("picture_controls.json").read_text(encoding="utf-8"))


def profile_index(directory):
    """Map Picture Control names to profiles in ``directory``.

    Release profiles are recognised by file name. Any other profile is matched by its own name, so a
    profile made with ``fit --name`` set to the NP3's name works too.
    """
    known = release_picture_controls()
    index = {}
    for path in sorted(Path(directory).rglob("*.xmp")):
        if path.name.startswith("._"):
            continue
        key = known.get(path.stem.removeprefix(RELEASE_PREFIX)) if path.stem.startswith(RELEASE_PREFIX) else None
        if key is None:
            try:
                key = read_profile(path)[1]["name"]
            except (ValueError, OSError):
                continue
        if key in index:
            raise ValueError(f"Two profiles match Picture Control {key!r}: {index[key]} and {path}")
        index[key] = path
    if not index:
        raise ValueError(f"No profiles found in {directory}")
    return index


def raw_files(paths, recursive=False):
    found = []
    for path in map(Path, paths):
        if path.is_dir():
            candidates = path.rglob("*") if recursive else path.iterdir()
            found += sorted(f for f in candidates if f.suffix.lower() in RAW_SUFFIXES and not f.name.startswith("._"))
        elif path.suffix.lower() in RAW_SUFFIXES:
            found.append(path)
        else:
            raise ValueError(f"Not a Nikon RAW file or folder: {path}")
    return found


def picture_controls(raws):
    """Return (path, Picture Control name or None) for each RAW, read with one ExifTool call."""
    if not raws:
        return []
    result = subprocess.run(
        ["exiftool", "-j", "-charset", "filename=utf8", "-PictureControlName", "-@", "-"],
        input="\n".join(str(p) for p in raws),
        capture_output=True,
        text=True,
        check=False,
    )
    if not result.stdout.strip():
        raise RuntimeError("ExifTool could not read the files: " + result.stderr.strip())
    names = {
        Path(row["SourceFile"]): str(row.get("PictureControlName", "")).strip() or None
        for row in json.loads(result.stdout)
    }
    return [(raw, names.get(raw)) for raw in raws]


def write_sidecars(paths, profiles, amount=1.0, overwrite=False, dry_run=False, recursive=False):
    index = profile_index(profiles)
    summary = dict(written=[], existing_sidecar=[], no_profile={}, no_picture_control=[])
    texts = {}
    for raw, name in picture_controls(raw_files(paths, recursive)):
        sidecar = raw.with_suffix(".xmp")
        if name is None:
            summary["no_picture_control"].append(str(raw))
        elif name not in index:
            summary["no_profile"][name] = summary["no_profile"].get(name, 0) + 1
        elif sidecar.exists() and not overwrite:
            summary["existing_sidecar"].append(str(sidecar))
        else:
            if name not in texts:
                texts[name] = import_sidecar(index[name], amount)
            if not dry_run:
                sidecar.write_text(texts[name], encoding="utf-8")
            summary["written"].append(dict(raw=str(raw), picture_control=name, profile=index[name].name))
    summary["dry_run"] = dry_run
    return summary
