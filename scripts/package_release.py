"""Create the release ZIPs: one per Camera Flexible Color body and one universal Adobe pack.

Does not commit, push or publish. Usage:
  python scripts/package_release.py --profiles /path/to/1.0-reference-profiles \
    --camera-profiles /path/to/camera-tables --previous-profiles /path/to/0.2.0/profiles \
    --output /path/to/release-assets

--camera-profiles holds one folder per fitted body (zf/, z9/, ...) with the profiles that
build_release_profiles.py --camera <body> wrote; docs/camera_manifests/<body>.json is checked against them.
"""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from nikon_recipes_lr import __version__
from nikon_recipes_lr.cameras import ADOBE, FLEX_CAMERAS, adobe_profile, camera_profile, table_sources
from nikon_recipes_lr.nx import sha256
from nikon_recipes_lr.profile import read_profile

ROOT = Path(__file__).resolve().parents[1]
PACK_NOTE = {
    "flex": (
        "This pack is for the **{label}**: its profiles are built on Camera Flexible Color{fitted_en} and appear only for photos from this camera.",
        "本压缩包适用于 **{label}**：配置文件以「相机 Flexible Color」为基础{fitted_zh}，只在这台相机拍摄的照片上显示。",
        "このパックは **{label}** 用です。プロファイルは Camera Flexible Color をベースにしており{fitted_ja}、このカメラの写真にだけ表示されます。",
    ),
    "adobe": (
        "This is the universal pack: its profiles are built on Adobe Standard and work with photos from any camera. For a Nikon body with Camera Flexible Color (Z 8, Z 9, Z f, Z6III, Z5II, Z50II, ZR), the pack for that camera is closer to NX Studio.",
        "这是通用版：配置文件以 Adobe Standard 为基础，适用于任何相机的照片。如果你的尼康机身有「相机 Flexible Color」（Z 8、Z 9、Z f、Z6III、Z5II、Z50II、ZR），对应机型的压缩包会更接近 NX Studio。",
        "これは汎用パックです。プロファイルは Adobe Standard をベースにしており、どのカメラの写真にも使えます。Camera Flexible Color のあるニコン機（Z 8、Z 9、Z f、Z6III、Z5II、Z50II、ZR）では、その機種用のパックのほうが NX Studio に近くなります。",
    ),
}


FITTED = dict(
    fitted_en=", with color tables measured on this camera's own RAW data,",
    fitted_zh="，色彩表由这台相机自己的 RAW 数据测量得到",
    fitted_ja="（カラーテーブルはこのカメラ自身の RAW データで測定）",
)
NOT_FITTED = dict(
    fitted_en=" (color tables measured on the Nikon Z 8)",
    fitted_zh="（色彩表在 Nikon Z 8 上测量）",
    fitted_ja="（カラーテーブルは Nikon Z 8 で測定）",
)


def readme(version, camera, kind):
    words = FITTED if camera.fitted else NOT_FITTED
    notes = [n.format(label=camera.label, **words) for n in PACK_NOTE[kind]]
    guides = [(ROOT / "docs" / lang / "INSTALL.md").read_text(encoding="utf-8").strip() for lang in ("en", "zh", "ja")]
    parts = [f"{note}\n\n{guide}" for note, guide in zip(notes, guides)]
    return f"# Nikon Recipes to LR Profiles {version} — {camera.label}\n\n" + "\n\n---\n\n".join(parts) + "\n"


def write_pack(destination, version, camera, kind, rows, texts):
    if destination.exists():
        raise FileExistsError(destination)
    manifest = []
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for row in rows:
            text = texts[row["recipe"]]
            archive.writestr("profiles/" + row["file"], text)
            data = text.encode("utf-8")
            entry = {k: row[k] for k in ("recipe", "display", "author", "group", "file", "fit", "banding")}
            entry.update(sha256=hashlib.sha256(data).hexdigest(), camera=camera.restriction, pack=camera.slug)
            manifest.append(entry)
        archive.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        archive.writestr("README.md", readme(version, camera, kind))
        for name in ("LICENSE", "PROFILE_LICENSE.md", "THIRD_PARTY_NOTICES.md"):
            archive.write(ROOT / name, name)
    return destination


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--profiles", required=True, help="Reference (Nikon Z 8) profiles of the current series")
    p.add_argument("--camera-profiles", required=True, help="Table sources of the fitted bodies, one folder each")
    p.add_argument("--previous-profiles", required=True, help="profiles/ of release 0.2.0, for the Adobe pack")
    p.add_argument("--output", required=True)
    p.add_argument("--version", default=__version__)
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    current = json.loads((ROOT / "docs/release_manifest.json").read_text(encoding="utf-8"))
    previous = json.loads((ROOT / "website/data/release_0.2.0_manifest.json").read_text(encoding="utf-8"))
    if len(current) != 236 or [r["recipe"] for r in previous] != [r["recipe"] for r in current]:
        raise ValueError("Both manifests must list the same 236 recipes")
    reference, prior = {}, {}
    for row in current:
        path = Path(args.profiles) / row["file"]
        if sha256(path) != row["sha256"] or read_profile(path)[1]["table_id"] != row["source_table_id"]:
            raise ValueError(f"Reference profile does not match the manifest: {path}")
        reference[row["recipe"]] = path.read_text(encoding="utf-8")
    for row in previous:
        path = Path(args.previous_profiles) / row["file"]
        if sha256(path) != row["sha256"]:
            raise ValueError(f"0.2.0 profile does not match its manifest: {path}")
        prior[row["recipe"]] = path.read_text(encoding="utf-8")
    sources = table_sources(args.camera_profiles, ROOT / "docs/camera_manifests")
    artifacts = []
    for camera in FLEX_CAMERAS:
        rows, tables = sources.get(camera.slug, (current, {}))
        if [r["recipe"] for r in rows] != [r["recipe"] for r in current]:
            raise ValueError(f"The {camera.slug} manifest lists different recipes")
        texts = {r: camera_profile(t, r, camera, tables.get(r)) for r, t in reference.items()}
        name = f"nikon-recipes-lr-profiles-{args.version}-{camera.slug}.zip"
        artifacts.append(write_pack(out / name, args.version, camera, "flex", rows, texts))
    texts = {r: adobe_profile(t, r) for r, t in prior.items()}
    name = f"nikon-recipes-lr-profiles-{args.version}-{ADOBE.slug}.zip"
    artifacts.append(write_pack(out / name, args.version, ADOBE, "adobe", previous, texts))
    print(json.dumps([dict(file=str(a), bytes=a.stat().st_size) for a in artifacts], indent=2))


if __name__ == "__main__":
    main()
