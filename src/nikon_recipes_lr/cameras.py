"""Camera packs of a release: one per body with a Camera Flexible Color profile, plus a universal Adobe pack.

The color table is the same for every Flexible Color body: Adobe's Camera Flexible Color for each camera
matches Nikon's Flexible Color on that camera, so the recipe's correction on top of it carries over. A
Lightroom profile can be restricted to only one camera model, so each body gets a copy with its own
restriction and UUID. Bodies without Camera Flexible Color, and other brands, use the Adobe pack: the
0.2 tables on Adobe Standard, without a camera restriction.

The release ZIPs and the website's per-recipe downloads are both made with these functions, so a profile
downloaded from either place is the same file.
"""

import re
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Camera:
    slug: str  # used in file and folder names
    label: str  # shown to people
    restriction: str  # crs:CameraModelRestriction, the model name Camera Raw uses


# The Z 8 keeps the restriction written in release 1.0.0, so its profiles stay byte-identical to 1.0.0.
FLEX_CAMERAS = (
    Camera("z8", "Nikon Z 8", "NIKON Z 8"),
    Camera("z9", "Nikon Z 9", "Nikon Z 9"),
    Camera("zf", "Nikon Z f", "Nikon Z f"),
    Camera("z6iii", "Nikon Z6III", "Nikon Z 6 3"),
    Camera("z5ii", "Nikon Z5II", "Nikon Z 5 2"),
    Camera("z50ii", "Nikon Z50II", "Nikon Z 50 2"),
    Camera("zr", "Nikon ZR", "Nikon ZR"),
)
ADOBE = Camera("adobe", "Other cameras (Adobe Standard)", "")
REFERENCE = FLEX_CAMERAS[0]
SERIES = "1.0"  # Profile Browser group and name suffix of this release series


def _once(pattern, replacement, text):
    result, count = re.subn(pattern, lambda _: replacement, text)
    if count != 1:
        raise ValueError(f"Expected exactly one match for {pattern!r}, found {count}")
    return result


def _uuid(*parts):
    return uuid.uuid5(uuid.NAMESPACE_URL, ":".join(("nikon-recipes-to-lr-profiles",) + parts)).hex.upper()


def camera_profile(reference_text, recipe, camera):
    """Turn the reference (Z 8) profile of a recipe into the profile for another Flexible Color body."""
    if camera == REFERENCE:
        return reference_text
    text = _once(
        r'crs:CameraModelRestriction="NIKON Z 8"', f'crs:CameraModelRestriction="{camera.restriction}"', reference_text
    )
    text = _once(r'crs:UUID="[0-9A-F]{32}"', f'crs:UUID="{_uuid(SERIES, camera.slug, recipe)}"', text)
    return _once(r"Camera Flexible Color, Nikon Z 8\)", f"Camera Flexible Color, {camera.label})", text)


def adobe_profile(previous_text, recipe):
    """Relabel a 0.2 profile (Adobe Standard base, no restriction) as the universal pack of this series."""
    tag = f"NRLR {SERIES} Adobe"
    text = previous_text.replace("[NRLR 0.2]", f"[{tag}]")
    if text.count(f"[{tag}]") != 3:
        raise ValueError("Expected the 0.2 suffix in Name, ShortName and SortName")
    text = _once(r"Nikon Recipes LR 0\.2/", f"Nikon Recipes LR {SERIES} Adobe/", text)
    text = _once(r'crs:UUID="[0-9A-F]{32}"', f'crs:UUID="{_uuid(SERIES, ADOBE.slug, recipe)}"', text)
    if 'crs:CameraProfile="Adobe Standard"' not in text or 'crs:CameraModelRestriction=""' not in text:
        raise ValueError("Expected an unrestricted profile on Adobe Standard")
    return text
