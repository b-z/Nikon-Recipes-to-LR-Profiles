"""Defensive reader for the observed NCP/NP3 TLV format; semantics remain Nikon-specific."""

import struct
from pathlib import Path


def parse_bytes(data):
    if len(data) > 16 * 1024 * 1024:
        raise ValueError("Recipe exceeds supported size")
    if data[:4] != b"NCP\0":
        raise ValueError("Not an NCP/NP3 recipe")
    records = []
    offset = 4
    while len(data) - offset > 4:
        if offset + 8 > len(data):
            raise ValueError("Truncated TLV header")
        tag, length = struct.unpack_from(">II", data, offset)
        offset += 8
        if length > len(data) - offset - 4:
            raise ValueError("Truncated TLV value or missing trailer")
        records.append((tag, data[offset : offset + length]))
        offset += length
    if len(data) - offset != 4:
        raise ValueError("Expected four-byte recipe trailer")
    return records, data[offset:]


def inspect(path):
    records, trailer = parse_bytes(Path(path).read_bytes())
    tags = dict(records)
    result = dict(
        version=tags.get(0x100, b"").rstrip(b"\0").decode("ascii", "replace"),
        name=tags.get(0x200, b"").rstrip(b"\0").decode("utf-8", "replace"),
        record_count=len(records),
        trailer=trailer.hex(),
        tags=[dict(tag=f"0x{t:06x}", length=len(v)) for t, v in records],
    )
    if 0x10100 in tags:
        result["creator_note"] = tags[0x10100].rstrip(b"\0").decode("utf-8", "replace")
    result["has_color_blender"] = 0x1F00 in tags
    result["has_color_grading"] = 0x2000 in tags
    result["has_explicit_tone_curve"] = 0x2 in tags and len(tags[0x2]) == 578
    return result
