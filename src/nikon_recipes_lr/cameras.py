"""Camera packs of a release: one per body with a Camera Flexible Color profile, plus a universal Adobe pack.

Every camera pack starts from the reference profile of a recipe (release 1.0, Nikon Z 8) and gets its own
name suffix, group, camera restriction and UUID. Bodies with a calibration kit (`calibration/<slug>/`) also
get their own color table, fitted on NX Studio exports of that body's chart: Camera Raw and NX Studio do not
place the brightness of every body in exactly the same way, and the Z 8 table carries that offset over.
Bodies without a kit keep the Z 8 table. Bodies without Camera Flexible Color, and other brands, use the
Adobe pack: the 0.2 tables on Adobe Standard, without a camera restriction.

The release ZIPs and the website's per-recipe downloads are both made with these functions, so a profile
downloaded from either place is the same file.
"""

import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Camera:
    slug: str  # used in file and folder names
    label: str  # shown to people
    restriction: str  # crs:CameraModelRestriction, the model name Camera Raw uses
    fitted: bool = False  # has its own calibration kit and color tables


# The Z 8 keeps the restriction written in release 1.0.0.
FLEX_CAMERAS = (
    Camera("z8", "Nikon Z 8", "NIKON Z 8", fitted=True),
    Camera("z9", "Nikon Z 9", "Nikon Z 9", fitted=True),
    Camera("zf", "Nikon Z f", "Nikon Z f", fitted=True),
    Camera("z6iii", "Nikon Z6III", "Nikon Z 6 3", fitted=True),
    Camera("z5ii", "Nikon Z5II", "Nikon Z 5 2", fitted=True),
    Camera("z50ii", "Nikon Z50II", "Nikon Z 50 2", fitted=True),
    Camera("zr", "Nikon ZR", "Nikon ZR", fitted=True),
)
ADOBE = Camera("adobe", "Other cameras (Adobe Standard)", "")
REFERENCE = FLEX_CAMERAS[0]
# Profiles carry the project's short name and the method's code name, not the release number: groups such as
# "NRLR Y9 - Stephen Morais" and names such as "KG200P1 by Stephen Morais [NRLR Y9]". Their UUIDs stay the same
# from release to release, so importing a newer release replaces the older profiles in Lightroom.
FLEX_CODE = "Y9"  # Camera Flexible Color packs
ADOBE_CODE = "Y8"  # Adobe Standard pack


def _once(pattern, replacement, text):
    result, count = re.subn(pattern, lambda _: replacement, text)
    if count != 1:
        raise ValueError(f"Expected exactly one match for {pattern!r}, found {count}")
    return result


def _uuid(*parts):
    return uuid.uuid5(uuid.NAMESPACE_URL, ":".join(("nikon-recipes-to-lr-profiles",) + parts)).hex.upper()


def profile_uuid(camera, recipe):
    return _uuid("nrlr", camera.slug, recipe)


def short_group(group):
    """A recipe's creator group as one short Profile Browser group: "ThirdParty/MGA/Nikon B&W Recipes" -> "MGA B&W Recipes"."""
    group = re.sub(r"^(Nikon Recipes LR[^/]*/)?(ThirdParty/)?", "", group)
    return group.replace("MGA/Nikon ", "MGA ").replace("/", " ")


def group_name(code, group):
    return f"NRLR {code} - {short_group(group)}"


def relabel(text, code, recipe, camera):
    """Give a release profile this project's names (suffix and group) and the camera pack's UUID."""
    text, count = re.subn(r"\[NRLR [^\]]*\]", f"[NRLR {code}]", text)
    if count != 3:
        raise ValueError("Expected the NRLR suffix in Name, ShortName and SortName")
    text, count = re.subn(
        r"(<crs:Group>\s*<rdf:Alt>\s*<rdf:li[^>]*>)([^<]*)(</rdf:li>)",
        lambda m: m.group(1) + group_name(code, m.group(2)) + m.group(3),
        text,
    )
    if count != 1:
        raise ValueError("Expected one profile group")
    return _once(r'crs:UUID="[0-9A-F]{32}"', f'crs:UUID="{profile_uuid(camera, recipe)}"', text)


TABLE = re.compile(r'crs:RGBTable="([0-9A-F]{32})"')


def table_of(text):
    """The table ID and the `crs:Table_<ID>="..."` attribute of a profile."""
    (tid,) = TABLE.findall(text)
    match = re.search(rf'crs:Table_{tid}="[^"]*"', text)
    if match is None:
        raise ValueError("Profile has no table data")
    return tid, match.group(0)


def camera_profile(reference_text, recipe, camera, table_source=None):
    """Turn the reference (Z 8) profile of a recipe into the profile for a Flexible Color body.

    ``table_source`` is a profile fitted on that body's calibration kit; its color table replaces the
    reference table. Everything else (names, credits, description) comes from the reference profile.
    """
    text = relabel(reference_text, FLEX_CODE, recipe, camera)
    text = _once(r'crs:CameraModelRestriction="NIKON Z 8"', f'crs:CameraModelRestriction="{camera.restriction}"', text)
    # Release descriptions name the camera; replace it where present.
    text = text.replace("Camera Flexible Color, Nikon Z 8)", f"Camera Flexible Color, {camera.label})")
    if table_source is not None:
        old_id, old_data = table_of(text)
        new_id, new_data = table_of(table_source)
        text = _once(re.escape(old_data), new_data, text)
        text = _once(f'crs:RGBTable="{old_id}"', f'crs:RGBTable="{new_id}"', text)
    return text


def table_sources(root, manifests):
    """Read the table-source profiles of every fitted body other than the reference.

    ``root`` holds one folder per body (``<root>/<slug>/<file>``), as written by
    ``scripts/build_release_profiles.py --camera <slug>``; ``manifests`` holds ``<slug>.json``, the manifest that
    script wrote. Returns ``{slug: (rows, {recipe: text})}`` and refuses files whose table differs from the manifest.
    """
    sources = {}
    for camera in FLEX_CAMERAS:
        if not camera.fitted or camera == REFERENCE:
            continue
        rows = json.loads((Path(manifests) / f"{camera.slug}.json").read_text(encoding="utf-8"))
        texts = {}
        for row in rows:
            path = Path(root) / camera.slug / row["file"]
            text = path.read_text(encoding="utf-8")
            if table_of(text)[0] != row["source_table_id"]:
                raise ValueError(f"Table does not match the {camera.slug} manifest: {path}")
            texts[row["recipe"]] = text
        sources[camera.slug] = (rows, texts)
    return sources


def adobe_profile(previous_text, recipe):
    """Relabel a 0.2 profile (Adobe Standard base, no restriction) as the universal pack."""
    text = relabel(previous_text, ADOBE_CODE, recipe, ADOBE)
    if 'crs:CameraProfile="Adobe Standard"' not in text or 'crs:CameraModelRestriction=""' not in text:
        raise ValueError("Expected an unrestricted profile on Adobe Standard")
    return text
