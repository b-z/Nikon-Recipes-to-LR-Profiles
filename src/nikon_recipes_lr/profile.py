"""Encode/decode Adobe RGBTable enhanced profiles; no Adobe SDK code bundled."""

import hashlib
import struct
import uuid
import xml.etree.ElementTree as ET
import zlib

import numpy as np

CRS = "http://ns.adobe.com/camera-raw-settings/1.0/"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
X = "adobe:ns:meta/"
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?`'|()[]{}@%$#"
URL = "https://github.com/b-z/Nikon-Recipes-to-LR-Profiles"
DEFAULT_GROUP = "Nikon Recipes LR/Custom"
DEFAULT_CAMERA = "NIKON Z 8"
for prefix, ns in [("x", X), ("rdf", RDF), ("crs", CRS)]:
    ET.register_namespace(prefix, ns)


def identity(n):
    if not 2 <= n <= 32:
        raise ValueError("RGBTable grid must be between 2 and 32")
    g = np.linspace(0, 1, n)
    return np.stack(np.meshgrid(g, g, g, indexing="ij"), -1)


def encode85(data):
    result = []
    for start in range(0, len(data), 4):
        word = int.from_bytes(data[start : start + 4].ljust(4, b"\0"), "little")
        for _ in range(5):
            result.append(ALPHABET[word % 85])
            word //= 85
    return "".join(result)


def decode85(text):
    text = "".join(text.split())
    if len(text) % 5:
        raise ValueError("Incomplete RGBTable base85 group")
    digits = {c: i for i, c in enumerate(ALPHABET)}
    output = bytearray()
    try:
        for start in range(0, len(text), 5):
            word = sum(digits[c] * 85**i for i, c in enumerate(text[start : start + 5]))
            if word > 0xFFFFFFFF:
                raise ValueError("RGBTable base85 word overflow")
            output.extend(word.to_bytes(4, "little"))
    except KeyError as exc:
        raise ValueError("Invalid RGBTable base85 character") from exc
    return bytes(output)


def _neutral(n):
    return np.array([(i * 65535 + (n >> 1)) // (n - 1) for i in range(n)], dtype=np.int64)


def pack_table(lut, amount_max=2.0):
    lut = np.asarray(lut, float)
    n = len(lut)
    if lut.shape != (n, n, n, 3) or not 2 <= n <= 32:
        raise ValueError("Expected (N,N,N,3), 2 <= N <= 32")
    if not np.isfinite(lut).all() or lut.min() < 0 or lut.max() > 1:
        raise ValueError("LUT must be finite and within 0..1")
    if not np.isfinite(amount_max) or amount_max <= 0:
        raise ValueError("Invalid maximum Amount")
    q = np.rint(lut * 65535).astype(np.int64)
    nv = _neutral(n)
    q -= np.stack(np.meshgrid(nv, nv, nv, indexing="ij"), -1)
    body = struct.pack("<4I", 1, 1, 3, n) + (q & 65535).astype("<u2").tobytes()
    body += struct.pack("<3I2d", 1, 3, 0, 0.0, amount_max)
    payload = struct.pack("<I", len(body)) + zlib.compress(body, 9)
    return encode85(payload), hashlib.md5(body).hexdigest().upper()


def unpack_table(payload):
    compressed = decode85(payload)
    if len(compressed) < 5:
        raise ValueError("Truncated RGBTable")
    size = struct.unpack_from("<I", compressed)[0]
    if not 44 <= size <= 44 + 32**3 * 6:
        raise ValueError("Unsupported RGBTable size")
    decoder = zlib.decompressobj()
    try:
        body = decoder.decompress(compressed[4:], size + 1)
    except zlib.error as exc:
        raise ValueError("Invalid compressed RGBTable") from exc
    if len(body) != size or not decoder.eof:
        raise ValueError("RGBTable stream length mismatch")
    kind, version, dims, n = struct.unpack_from("<4I", body)
    if (kind, version, dims) != (1, 1, 3) or not 2 <= n <= 32 or size != 44 + n**3 * 6:
        raise ValueError("Unsupported RGBTable header")
    rel = np.frombuffer(body, dtype="<u2", count=n**3 * 3, offset=16).reshape(n, n, n, 3).astype(np.int64)
    nv = _neutral(n)
    rel += np.stack(np.meshgrid(nv, nv, nv, indexing="ij"), -1)
    primaries, gamma, gamut, amin, amax = struct.unpack_from("<3I2d", body, 16 + n**3 * 6)
    if (primaries, gamma, gamut) != (1, 3, 0):
        raise ValueError("This tool supports encoded Adobe RGB with clipped gamut only")
    if not 0 <= amin < amax or not np.isfinite(amax):
        raise ValueError("Invalid Amount range")
    return (rel & 65535) / 65535.0, dict(
        grid=n,
        primaries=primaries,
        gamma=gamma,
        gamut=gamut,
        amount_min=amin,
        amount_max=amax,
        table_id=hashlib.md5(body).hexdigest().upper(),
    )


def read_profile(path):
    root = ET.parse(path).getroot()
    desc = root.find(f".//{{{RDF}}}Description")
    if desc is None:
        raise ValueError("Missing XMP description")
    tid = desc.get(f"{{{CRS}}}RGBTable")
    payload = desc.get(f"{{{CRS}}}Table_{tid}")
    if not tid or not payload:
        raise ValueError("Profile has no embedded RGBTable")
    lut, metadata = unpack_table(payload)
    if metadata["table_id"] != tid.upper():
        raise ValueError("RGBTable fingerprint mismatch")

    def field(name):
        el = desc.find(f"{{{CRS}}}{name}/{{{RDF}}}Alt/{{{RDF}}}li")
        return el.text if el is not None else ""

    metadata.update(
        name=field("Name"),
        group=field("Group"),
        uuid=desc.get(f"{{{CRS}}}UUID"),
        base=desc.get(f"{{{CRS}}}CameraProfile"),
        camera=desc.get(f"{{{CRS}}}CameraModelRestriction", ""),
        payload=payload,
    )
    return lut, metadata


def build_profile(lut, name, author, group=DEFAULT_GROUP, camera=DEFAULT_CAMERA):
    """Return an enhanced-profile XMP (Look on Adobe Standard) embedding ``lut``.

    The UUID is derived from the group and name, so re-fitting a profile with the
    same name and group replaces it in Lightroom instead of adding a duplicate.
    """
    payload, tid = pack_table(lut)
    root = ET.Element(f"{{{X}}}xmpmeta")
    rdf = ET.SubElement(root, f"{{{RDF}}}RDF")
    attrs = dict(
        PresetType="Look",
        Cluster="Nikon Recipes to LR Profiles",
        UUID=uuid.uuid5(uuid.NAMESPACE_URL, f"{URL}:{group}:{name}").hex.upper(),
        SupportsAmount="True",
        SupportsColor="True",
        SupportsMonochrome="False",
        SupportsHighDynamicRange="True",
        SupportsNormalDynamicRange="True",
        SupportsSceneReferred="True",
        SupportsOutputReferred="True",
        RequiresRGBTables="False",
        CameraModelRestriction=camera,
        Copyright=f"Original recipe by {author}; conversion by Nikon Recipes to LR Profiles.",
        ContactInfo=URL,
        Version="15.4",
        ProcessVersion="15.4",
        ConvertToGrayscale="False",
        CameraProfile="Adobe Standard",
        RGBTable=tid,
        RGBTableAmount="1.000000",
        HasSettings="True",
    )
    attrs[f"Table_{tid}"] = payload
    desc = ET.SubElement(rdf, f"{{{RDF}}}Description", {f"{{{CRS}}}{k}": v for k, v in attrs.items()})
    description = (
        f"Original recipe by {author}. Calibrated approximation on Adobe Standard made with Nikon Recipes to LR Profiles ({URL}); Amount 0–200%."
        + (f" Calibrated for {camera}." if camera else "")
    )
    for key, value in [
        ("Name", name),
        ("ShortName", name),
        ("SortName", name),
        ("Group", group),
        ("Description", description),
    ]:
        element = ET.SubElement(desc, f"{{{CRS}}}{key}")
        alt = ET.SubElement(element, f"{{{RDF}}}Alt")
        ET.SubElement(alt, f"{{{RDF}}}li", {"{http://www.w3.org/XML/1998/namespace}lang": "x-default"}).text = value
    return ET.tostring(root, encoding="unicode") + "\n"


def render_sidecar(profile=None, amount=1.0):
    if not 0 <= amount <= 2 or not np.isfinite(amount):
        raise ValueError("Amount must be 0..2")
    root = ET.Element(f"{{{X}}}xmpmeta")
    rdf = ET.SubElement(root, f"{{{RDF}}}RDF")
    settings = dict(
        Version="18.3",
        ProcessVersion="15.4",
        CameraProfile="Adobe Standard",
        WhiteBalance="As Shot",
        HasSettings="True",
        ToneCurveName2012="Linear",
        ToneCurvePV2012="0, 0, 255, 255",
    )
    for k in (
        "Exposure2012",
        "Contrast2012",
        "Highlights2012",
        "Shadows2012",
        "Whites2012",
        "Blacks2012",
        "Texture",
        "Clarity2012",
        "Dehaze",
        "Vibrance",
        "Saturation",
        "Sharpness",
        "LuminanceSmoothing",
        "ColorNoiseReduction",
        "LensProfileEnable",
        "AutoLateralCA",
        "VignetteAmount",
        "GrainAmount",
    ):
        settings[k] = "0"
    desc = ET.SubElement(rdf, f"{{{RDF}}}Description", {f"{{{CRS}}}{k}": v for k, v in settings.items()})
    if profile:
        _, m = read_profile(profile)
        if m["base"] != "Adobe Standard":
            raise ValueError("Expected Adobe Standard profile")
        look = ET.SubElement(desc, f"{{{CRS}}}Look")
        ld = ET.SubElement(
            look,
            f"{{{RDF}}}Description",
            {
                f"{{{CRS}}}{k}": str(v)
                for k, v in dict(
                    Name=m["name"],
                    UUID=m["uuid"],
                    Amount=amount,
                    SupportsAmount="true",
                    SupportsMonochrome="false",
                    SupportsOutputReferred="true",
                ).items()
            },
        )
        params = ET.SubElement(ld, f"{{{CRS}}}Parameters")
        ET.SubElement(
            params,
            f"{{{RDF}}}Description",
            {
                f"{{{CRS}}}{k}": v
                for k, v in dict(
                    Version="15.4",
                    ProcessVersion="15.4",
                    ConvertToGrayscale="False",
                    CameraProfile=m["base"],
                    RGBTable=m["table_id"],
                    RGBTableAmount="1.000000",
                    **{f"Table_{m['table_id']}": m["payload"]},
                ).items()
            },
        )
    return ET.tostring(root, encoding="unicode") + "\n"
