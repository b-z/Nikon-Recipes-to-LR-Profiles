"""Experimental Z8 chart generator. Requires the original calibration donor's metadata."""

import colorsys
import json
import struct
import subprocess
from pathlib import Path

import numpy as np

W, H = 8280, 5520
INSET = (12, 8)
BLACK = 1008
WHITE_LIMIT = 15311
WB = np.array([1.85156, 1.0, 1.42578])
CAM2SRGB = np.array([[1.3931, -0.2157, -0.1774], [-0.1364, 1.4786, -0.3423], [-0.0256, -0.3210, 1.3466]])
SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}


def chart():
    saturation = np.r_[0.006, 0.012, 0.022, 0.040, 0.070, 0.105, 0.150, 0.200, np.linspace(0.27, 1.0, 13)]
    patches = []
    labels = []
    for iv, v in enumerate(np.linspace(0.03, 1.0, 24)):
        for isat, s in enumerate(saturation):
            for ih, h in enumerate(np.linspace(0, 1, 48, endpoint=False)):
                patches.append(colorsys.hsv_to_rgb(h, s, v))
                labels.append(f"x{iv}_{isat}_{ih}")
    for k, g in enumerate(np.linspace(0.02, 1.0, 60)):
        for r in range(4):
            patches.append((g, g, g))
            labels.append(f"n{k}_{r}")
    return np.array(patches), labels


def _ifd(data, offset):
    if offset < 8 or offset + 2 > len(data):
        raise ValueError("Invalid donor IFD offset")
    count = struct.unpack_from("<H", data, offset)[0]
    if offset + 2 + count * 12 + 4 > len(data):
        raise ValueError("Truncated donor IFD")
    entries = {}
    for i in range(count):
        start = offset + 2 + 12 * i
        tag, kind, n = struct.unpack_from("<HHI", data, start)
        if kind not in SIZES:
            raise ValueError("Unsupported donor TIFF type")
        entries[tag] = (kind, n, start + 8)
    return entries


def _values(data, entries, tag):
    kind, n, offset = entries[tag]
    formats = {1: "B", 3: "H", 4: "I"}
    if kind not in formats:
        raise ValueError("Unsupported donor integer tag")
    if SIZES[kind] * n > 4:
        offset = struct.unpack_from("<I", data, offset)[0]
    if offset + SIZES[kind] * n > len(data):
        raise ValueError("Donor tag out of bounds")
    return struct.unpack_from("<" + str(n) + formats[kind], data, offset)


def generate(donor, output, confirm_calibration=False):
    """Replace a trailing single Z8 raw strip; previews intentionally remain donor previews."""
    if not confirm_calibration:
        raise ValueError("Explicit --confirm-donor-calibration required; see docs/en/calibration.md")
    output = Path(output)
    meta = output.with_suffix(".json")
    if output.exists() or meta.exists():
        raise FileExistsError(output)
    info = json.loads(subprocess.check_output(["exiftool", "-j", "-Model", str(donor)]))[0]
    if info.get("Model") != "NIKON Z 8":
        raise ValueError("Only NIKON Z 8 donors are supported")
    data = bytearray(Path(donor).read_bytes())
    if data[:4] != b"II*\x00":
        raise ValueError("Expected little-endian Nikon TIFF container")
    first = _ifd(data, struct.unpack_from("<I", data, 4)[0])
    raw_ifds = []
    for off in _values(data, first, 330):
        entries = _ifd(data, off)
        if (
            256 in entries
            and 257 in entries
            and _values(data, entries, 256) == (W,)
            and _values(data, entries, 257) == (H,)
        ):
            raw_ifds.append(entries)
    if len(raw_ifds) != 1:
        raise ValueError("No unique full-resolution Z8 raw IFD")
    raw = raw_ifds[0]
    offsets = _values(data, raw, 273)
    counts = _values(data, raw, 279)
    if len(offsets) != 1 or len(counts) != 1 or offsets[0] + counts[0] != len(data):
        raise ValueError("Requires a single raw strip at EOF")
    for tag in (259, 279):
        kind, n, _ = raw[tag]
        if n != 1 or kind not in (3, 4):
            raise ValueError("Unsupported raw strip tag layout")
    rgb, labels = chart()
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    camera = np.einsum("...j,ij->...i", linear, np.linalg.inv(CAM2SRGB))
    codes = BLACK + np.maximum(camera, 0) / WB * ((WHITE_LIMIT - BLACK) * 0.95)
    if not np.isfinite(codes).all():
        raise ValueError("Nonfinite synthetic raw values")
    codes = np.rint(np.clip(codes, 0, 16383)).astype("<u2")
    pitch = 40
    cols = (W - INSET[0]) // pitch
    if INSET[1] + int(np.ceil(len(rgb) / cols)) * pitch > H:
        raise ValueError("Chart overflow")
    image = np.full((H, W), BLACK, dtype="<u2")
    patches = []
    for i, (r, g, b) in enumerate(codes):
        row, col = divmod(i, cols)
        x = INSET[0] + col * pitch
        y = INSET[1] + row * pitch
        block = image[y : y + pitch, x : x + pitch]
        block[::2, ::2] = r
        block[::2, 1::2] = g
        block[1::2, ::2] = g
        block[1::2, 1::2] = b
        patches.append(dict(label=labels[i], center=[x + pitch // 2, y + pitch // 2], srgb=rgb[i].tolist()))
    for tag, value in [(259, 1), (279, image.nbytes)]:
        kind, _, pos = raw[tag]
        struct.pack_into("<" + {3: "H", 4: "I"}[kind], data, pos, value)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as f:
        f.write(data[: offsets[0]])
        image.tofile(f)
    del image, data
    subprocess.run(
        [
            "exiftool",
            "-q",
            "-overwrite_original",
            "-Nikon:ActiveD-Lighting=Off",
            "-Nikon:VignetteControl=Off",
            "-Nikon:AutoDistortionControl=Off",
            "-Nikon:DiffractionCompensation=Off",
            str(output),
        ],
        check=True,
    )
    meta.write_text(
        json.dumps(
            dict(
                sensor_size=[W, H],
                active_size=[8256, 5504],
                inset=list(INSET),
                pitch=pitch,
                patches=patches,
                preview_warning="Embedded JPEG previews are donor previews; render the raw data",
            ),
            indent=2,
        ),
        encoding="utf-8",
    )
    return meta
