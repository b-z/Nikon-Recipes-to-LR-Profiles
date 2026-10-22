"""Write src/nikon_recipes_lr/picture_controls.json: release recipe ID -> Picture Control name of its NP3.

The camera records this name in each NEF, and ``nikon-recipes-lr sidecars`` uses it to find the
matching profile. Run it whenever the release manifest gains or renames recipes.

Usage: python scripts/write_picture_controls.py /path/to/Nikon-Recipes-archive
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nikon_recipes_lr.np3 import inspect  # noqa: E402


def main():
    archive = Path(sys.argv[1])
    recipes = [row["recipe"] for row in json.loads((ROOT / "docs/release_manifest.json").read_text(encoding="utf-8"))]
    # Recipe IDs are the archive's NP3 file names with spaces replaced by underscores.
    np3 = {p.stem.replace(" ", "_"): p for p in archive.rglob("*") if p.suffix.lower() == ".np3"}
    missing = [r for r in recipes if r not in np3]
    if missing:
        raise SystemExit(f"NP3 not found in the archive for: {', '.join(missing)}")
    names = {r: inspect(np3[r])["name"] for r in sorted(recipes, key=str.lower)}
    repeated = {n for n in names.values() if list(names.values()).count(n) > 1}
    if repeated:
        raise SystemExit(f"Picture Control names used by more than one recipe: {sorted(repeated)}")
    out = ROOT / "src/nikon_recipes_lr/picture_controls.json"
    out.write_text(json.dumps(names, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(names)} recipes -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
