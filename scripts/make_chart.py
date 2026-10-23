"""Make a calibration chart for another Nikon body from one of its RAW files.

The chart of every kit holds the same 24,720 raw patch values as the Z 8 chart, written into a NEF from the
other body so that NX Studio and Camera Raw treat it as that camera. Two steps:

  python scripts/make_chart.py build --donor /path/to/any-photo.NEF --pitch 30 --output calibration/<body>
  # render calibration/<body>/chart.NEF with NX Studio or Camera Raw as a 16-bit Adobe RGB TIFF, then
  python scripts/make_chart.py align --tiff /path/to/render.tif --kit calibration/<body>

`build` writes chart.NEF and chart.json. The donor must be an uncompressed or lossless compressed 14-bit NEF
(not High Efficiency) at full size; pick the largest pitch at which the 24,720 patches fit (40 for 45 MP,
30 for 24 MP, 28 for 20 MP). It switches off Active D-Lighting, vignette control, distortion control and
diffraction compensation, sets Adobe RGB and the normal orientation, and turns mandatory lens distortion
correction (some Z lenses) into the optional kind so that the chart is not warped.

`align` finds where the patches lie in the rendered TIFF (the renderers crop a few pixels from the sensor
edge) and writes that offset into chart.json; check that NX Studio and Camera Raw renders give the same result.
Then render the chart with Camera Raw and measure it with `nikon-recipes-lr sample` to get the kit's
camera-flexible-color.npy, as described in calibration/z8/README.md.
"""

import argparse
import json
import re
import struct
import subprocess
import zipfile
from pathlib import Path

import numpy as np
import tifffile

from nikon_recipes_lr.target import _ifd, _values

ROOT = Path(__file__).resolve().parents[1]
Z8 = ROOT / "calibration/z8"
BLACK = 1008


def reference_codes():
    """The raw RGGB values of every patch, read from the Z 8 chart."""
    meta = json.loads((Z8 / "chart.json").read_text(encoding="utf-8"))
    with zipfile.ZipFile(Z8 / "chart.NEF.zip") as archive:
        data = archive.read("chart.NEF")
    raw = _raw_ifd(data)
    width, height = _values(data, raw, 256)[0], _values(data, raw, 257)[0]
    (offset,) = _values(data, raw, 273)
    image = np.frombuffer(data, "<u2", width * height, offset).reshape(height, width)
    codes = []
    for patch in meta["patches"]:
        x, y = patch["center"]
        x, y = x - x % 2, y - y % 2  # top-left of an RGGB quad
        codes.append((image[y, x], image[y, x + 1], image[y + 1, x + 1]))
    return meta, np.array(codes, dtype="<u2")


def _raw_ifd(data):
    first = _ifd(data, struct.unpack_from("<I", data, 4)[0])
    for offset in _values(data, first, 330):
        entries = _ifd(data, offset)
        if 256 in entries and _values(data, entries, 256)[0] > 1000:
            return entries
    raise ValueError("No full-size raw image in the NEF")


def build(donor, pitch, output):
    output.mkdir(parents=True, exist_ok=True)
    meta, codes = reference_codes()
    data = bytearray(donor.read_bytes())
    raw = _raw_ifd(data)
    width, height = _values(data, raw, 256)[0], _values(data, raw, 257)[0]
    (offset,), (count,) = _values(data, raw, 273), _values(data, raw, 279)
    if offset + count != len(data):
        raise ValueError("The raw data is not the last part of the file; use another NEF from this camera")
    if _values(data, raw, 259)[0] not in (1, 34713) or _values(data, raw, 258)[0] != 14:
        raise ValueError("Use an uncompressed or lossless compressed 14-bit NEF")
    inset = (12, 8)
    cols, rows = (width - 2 * inset[0]) // pitch, (height - 2 * inset[1]) // pitch
    if cols * rows < len(codes):
        raise ValueError(f"{len(codes)} patches do not fit at pitch {pitch}; use a smaller pitch")
    image = np.full((height, width), BLACK, dtype="<u2")
    patches = []
    for i, (r, g, b) in enumerate(codes):
        row, col = divmod(i, cols)
        x, y = inset[0] + col * pitch, inset[1] + row * pitch
        block = image[y : y + pitch, x : x + pitch]
        block[::2, ::2], block[::2, 1::2], block[1::2, ::2], block[1::2, 1::2] = r, g, g, b
        patches.append(dict(label=meta["patches"][i]["label"], center=[x + pitch // 2, y + pitch // 2]))
    for tag, value in [(259, 1), (279, image.nbytes)]:
        kind, _, position = raw[tag]
        struct.pack_into("<" + {3: "H", 4: "I"}[kind], data, position, value)
    nef = output / "chart.NEF"
    nef.write_bytes(bytes(data[:offset]) + image.tobytes())
    settings = ["-Nikon:ActiveD-Lighting=Off", "-Nikon:VignetteControl=Off", "-Nikon:AutoDistortionControl=Off"]
    settings += ["-Nikon:DiffractionCompensation=Off", "-Nikon:ColorSpace=Adobe RGB", "-IFD0:Orientation#=1"]
    subprocess.run(["exiftool", "-q", "-m", "-overwrite_original", *settings, str(nef)], check=True)
    _optional_distortion_correction(nef)
    chart = dict(sensor_size=[width, height], active_size=None, inset=None, pitch=pitch)
    chart["preview_warning"] = "Embedded JPEG previews are donor previews; render the raw data"
    chart["patches"] = patches
    (output / "chart.json").write_text(json.dumps(chart), encoding="utf-8")
    print(f"{nef}: {width}x{height}, {cols}x{rows} patches of {pitch} px. Render it, then run `align`.")


def _optional_distortion_correction(nef):
    """Mandatory distortion correction (value 3) cannot be switched off in NX Studio; mark it optional (2)."""
    verbose = subprocess.run(["exiftool", "-v3", str(nef)], capture_output=True, text=True, check=True).stdout
    match = re.search(r"DistortionCorrection = 3\n.*?\n.*?([0-9a-f]+): 03", verbose)
    if match:
        position = int(match.group(1), 16)
        with nef.open("r+b") as f:
            f.seek(position)
            if f.read(1) != b"\x03":
                raise ValueError("Unexpected DistortionCorrection layout")
            f.seek(position)
            f.write(b"\x02")
        print("Mandatory distortion correction changed to optional")


def align(tiff, kit):
    path = kit / "chart.json"
    chart = json.loads(path.read_text(encoding="utf-8"))
    image = tifffile.imread(tiff).astype(np.float32)
    height, width = image.shape[:2]
    centers = np.array([p["center"] for p in chart["patches"]])[::37]
    r = chart["pitch"] // 2 - 3
    best = None
    for ox in range(-4, 33):
        for oy in range(-4, 33):
            spreads = [
                image[y - oy - r : y - oy + r + 1, x - ox - r : x - ox + r + 1].reshape(-1, 3).std(0).mean()
                for x, y in centers
                if r <= x - ox < width - r and r <= y - oy < height - r
            ]
            if len(spreads) > 0.95 * len(centers) and (best is None or np.mean(spreads) < best[0]):
                best = (float(np.mean(spreads)), ox, oy)
    if best is None:
        raise ValueError("The patches were not found; is the TIFF a full-size render of this chart?")
    chart["active_size"], chart["inset"] = [width, height], [best[1], best[2]]
    path.write_text(json.dumps(chart), encoding="utf-8")
    print(f"Patches found at offset {chart['inset']} (spread {best[0]:.1f}); written to {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="Write chart.NEF and chart.json")
    b.add_argument("--donor", type=Path, required=True, help="Lossless or uncompressed 14-bit NEF from the body")
    b.add_argument("--pitch", type=int, required=True, help="Patch size in pixels")
    b.add_argument("--output", type=Path, required=True, help="Kit folder, e.g. calibration/zr")
    a = sub.add_parser("align", help="Find the patch offset in a rendered TIFF")
    a.add_argument("--tiff", type=Path, required=True)
    a.add_argument("--kit", type=Path, required=True)
    args = p.parse_args()
    if args.command == "build":
        build(args.donor, args.pitch, args.output)
    else:
        align(args.tiff, args.kit)


if __name__ == "__main__":
    main()
