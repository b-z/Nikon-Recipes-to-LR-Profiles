"""Make the gallery's preview images: every source at the same size and through the same steps.

Inputs, all supplied explicitly:
  --renders DIR   16-bit Adobe RGB TIFFs of the four sample NEFs rendered by Camera Raw without a recipe, named
                  <scene>_adobe-standard.tif and <scene>_camera-flexible-color.tif, e.g.
                  nikon-recipes-lr render _DSC9046.NEF --base "Camera Flexible Color" --output 9046_camera-flexible-color.tif
                  (_DSC5054: render a copy whose Nikon DistortionCorrection tag is 2 instead of 3, so the geometry
                  matches NX Studio.)
  --nx DIR        NX Studio JPEG exports at original size, named <scene>_<recipe>.jpg
  --profiles DIR, --previous-profiles DIR   profiles/ folders of the current and the 0.2.0 release ZIP

Each render is averaged over 6×6 pixel blocks, the profile's table is applied to every pixel, and the result is
converted to sRGB and resized to WIDTH pixels; NX exports are converted and resized the same way. Output:
  images/{y9,y8}/<scene>_<recipe>.jpg, images/{adobe,flex}/<scene>.jpg, images/nx/<scene>_<recipe>.jpg,
  images/thumbs/<recipe>.jpg (from the current release on scene 9046). Existing files are kept.
"""

import argparse
import io
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, ImageCms

from nikon_recipes_lr.profile import read_profile
from nikon_recipes_lr.tetrahedral import vertices

ROOT = Path(__file__).resolve().parents[2]
SCENES = ("9046", "2849", "2694", "5054")
BASES = {"adobe": "adobe-standard", "flex": "camera-flexible-color"}
# Release folder name -> (base profile of its looks, manifest)
VERSIONS = {
    "y9": ("flex", ROOT / "docs/release_manifest.json"),
    "y8": ("adobe", ROOT / "website/data/release_0.2.0_manifest.json"),
}
WIDTH = 1280


def srgb():
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))


def save(pic, path, quality=86):
    path.parent.mkdir(parents=True, exist_ok=True)
    pic.save(path, quality=quality, icc_profile=srgb().tobytes())


def resized(pic):
    return pic.resize((WIDTH, round(WIDTH * pic.height / pic.width)), Image.Resampling.LANCZOS)


def load_render(path):
    """Read a 16-bit render, average 6×6 blocks, and return (array 0..1, ICC bytes)."""
    with tifffile.TiffFile(path) as tif:
        icc = tif.pages[0].tags[34675].value
        image = tif.pages[0].asarray()
    h, w = image.shape[0] // 6 * 6, image.shape[1] // 6 * 6
    blocks = image[:h, :w].astype("f4").reshape(h // 6, 6, w // 6, 6, 3).mean((1, 3)) / 65535
    return blocks, icc


def to_srgb(array, icc):
    pic = Image.fromarray(np.rint(np.clip(array, 0, 1) * 255).astype("u1"))
    return ImageCms.profileToProfile(pic, ImageCms.ImageCmsProfile(io.BytesIO(icc)), srgb(), outputMode="RGB")


class Applier:
    """Apply many 32³ tables to one image with tetrahedral interpolation, reusing the vertex weights."""

    def __init__(self, image):
        self.shape = image.shape
        corners, weights = vertices(image.reshape(-1, 3), 32)
        self.index = ((corners[..., 0] * 32 + corners[..., 1]) * 32 + corners[..., 2]).astype("i4")
        self.weights = weights.astype("f4")

    def __call__(self, lut):
        table = lut.reshape(-1, 3).astype("f4")
        return np.einsum("nk,nkc->nc", self.weights, table[self.index]).reshape(self.shape)


def scene_job(args):
    renders, out, profiles, scene = args
    images = out / "images"
    bases = {key: load_render(renders / f"{scene}_{name}.tif") for key, name in BASES.items()}
    for key, (array, icc) in bases.items():
        if not (images / key / f"{scene}.jpg").exists():
            save(resized(to_srgb(array, icc)), images / key / f"{scene}.jpg")
    appliers = {key: Applier(array) for key, (array, _) in bases.items()}
    count = 0
    for version, (base, manifest) in VERSIONS.items():
        for row in json.loads(manifest.read_text(encoding="utf-8")):
            path = images / version / f"{scene}_{row['recipe']}.jpg"
            if path.exists():
                continue
            lut, _ = read_profile(profiles[version] / row["file"])
            pic = resized(to_srgb(appliers[base](lut), bases[base][1]))
            save(pic, path)
            if version == "y9" and scene == "9046":
                thumb = pic.copy()
                thumb.thumbnail((240, 160), Image.Resampling.LANCZOS)
                save(thumb, images / "thumbs" / f"{row['recipe']}.jpg", 82)
            count += 1
    return scene, count


def nx_previews(nx, out):
    for ref in json.loads((ROOT / "website/data/nx_references.json").read_text(encoding="utf-8")):
        dest = out / ref["path"]
        if dest.exists():
            continue
        with Image.open(nx / f"{ref['photo']}_{ref['recipe']}.jpg") as pic:
            pic.draft("RGB", (pic.width // 4, pic.height // 4))
            icc = pic.info.get("icc_profile")
            rgb = pic.convert("RGB")
            if icc:
                rgb = ImageCms.profileToProfile(
                    rgb, ImageCms.ImageCmsProfile(io.BytesIO(icc)), srgb(), outputMode="RGB"
                )
            save(resized(rgb), dest)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--renders", type=Path, required=True)
    p.add_argument("--nx", type=Path, required=True)
    p.add_argument("--profiles", type=Path, required=True)
    p.add_argument("--previous-profiles", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True, help="Image library root; images/ is created inside")
    p.add_argument("--scenes", nargs="+", default=list(SCENES))
    p.add_argument("--workers", type=int, default=2, help="Parallel scenes; each needs several GB of memory")
    args = p.parse_args()
    profiles = {"y9": args.profiles, "y8": args.previous_profiles}
    nx_previews(args.nx, args.output)
    with ProcessPoolExecutor(args.workers) as pool:
        for scene, count in pool.map(scene_job, [(args.renders, args.output, profiles, s) for s in args.scenes]):
            print(f"scene {scene}: {count} previews", flush=True)


if __name__ == "__main__":
    main()
