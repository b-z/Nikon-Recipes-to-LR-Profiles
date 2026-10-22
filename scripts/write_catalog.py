"""Write docs/RECIPES.md and docs/recipes/*.md from the release manifest.

The catalog describes the profiles shipped in the current Release
(docs/release_manifest.json). Previous-version scores are shown for comparison
only. Actual Camera Raw checks are listed only when their table ID matches the
shipped table.
"""

import html
import json
from pathlib import Path
from urllib.parse import quote

from nikon_recipes_lr import __version__

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GALLERY = "https://nikon-recipes-to-lr-profiles.pages.dev/"


# Reader-facing wording for the manifest's review and measurement fields, which keep their original values.
REVIEW = {
    True: "This recipe showed banding in an earlier version (Y7). The 0.2 version was checked on several real photographs "
    "and no banding was seen; 1.0 uses the same fitting settings and has a lower banding-risk score, but has not been "
    "reviewed photo by photo.",
    False: "Not reviewed photo by photo.",
}
POLICY = {
    "original NX chart; detail settings not uniformly disabled": "NX Studio chart render with the recipe's own detail settings",
    "verified detail-off NX chart": "NX Studio chart render with detail settings switched off",
}


def main():
    rows = json.loads((DOCS / "release_manifest.json").read_text(encoding="utf-8"))
    version = __version__
    checks = {}
    for name in ("acr_validation.json", "y8_acr_validation.json"):
        for check in json.loads((DOCS / name).read_text(encoding="utf-8")):
            checks.setdefault((check["recipe"], check["table_id"]), []).append(check)
    previous = rows[0]["previous"]["version"]
    under_one = sum(row["fit"]["mean"] < 1 for row in rows)
    index = [
        f"# Recipe catalog — {version}",
        "",
        f"All {len(rows)} profiles of release {version}, with their creators and two scores. "
        "[Compare every recipe on four photographs in the online gallery]({GALLERY}).".format(GALLERY=GALLERY),
        "",
        "- **Difference from NX Studio**: the average color difference (CIEDE2000 ΔE) to NX Studio on the test chart. "
        f"About 1 is the smallest difference most people notice; {under_one} of {len(rows)} recipes are below 1.",
        "- **Banding risk**: how abruptly the color table changes direction (face-jump p99). Lower means smoother "
        "gradients, but no score guarantees a smooth sky in every photo.",
        f"- The {previous} columns show the previous release for comparison. [How the scores are measured](en/metrics.md).",
        "",
        f"| Recipe / creator | Difference from NX | Banding risk | {previous} difference | {previous} banding risk |",
        "|---|---:|---:|---:|---:|",
    ]
    pages = DOCS / "recipes"
    pages.mkdir(exist_ok=True)
    for row in rows:
        recipe = row["recipe"]
        fit = row["fit"]
        risk = row["banding"]
        old = row["previous"]
        author = html.escape(row["author"])
        display = html.escape(row["display"])
        index.append(
            f"| [{display} — {author}](recipes/{quote(recipe, safe='')}.md) | {fit['mean']:.2f} | "
            f"{risk['face_jump_p99']:.2f} | {old['fit_mean']:.2f} | {old['face_jump_p99']:.2f} |"
        )
        page = f"""# {display}

Recipe by **{author}**. [Original NP3 archive]({row["input_recipe_source"]}) · [All recipes](../RECIPES.md) · [See it in the gallery]({GALLERY}#{quote(recipe, safe="")})

Profile file `{row["file"]}` in release {version}, on the **{row["base"]}** base profile. Scores are at 100% Amount.

| Measurement | {version} | {old["version"]} |
|---|---:|---:|
| Difference from NX Studio, chart mean ΔE | {fit["mean"]:.3f} | {old["fit_mean"]:.3f} |
| Chart median ΔE | {fit["median"]:.3f} | — |
| Chart p95 ΔE (the 5% largest differences start here) | {fit["p95"]:.3f} | {old["fit_p95"]:.3f} |
| Chart mean ΔE on patches left out of the fit | {fit["heldout"]["mean"]:.3f} | — |
| Banding risk, face-jump p99 | {risk["face_jump_p99"]:.3f} | {old["face_jump_p99"]:.3f} |
| Face-jump maximum / RMS | {risk["face_jump_max"]:.3f} / {risk["face_jump_rms"]:.3f} | — |
| Chart patches used | {fit["sample_count"]} | |

Visual review: {REVIEW[row["prior_y7_banding"]]} Reference: {POLICY[row["measurement_policy"]]}.

The scores describe the profile on the test chart; a low difference does not guarantee smooth skies or bokeh in every photo. [What the scores mean](../en/metrics.md).

"""
        verified = checks.get((recipe, row["source_table_id"]), [])
        if verified:
            page += "## Camera Raw check\n\nThis table was rendered through Camera Raw and compared with the gallery preview: "
            page += ", ".join(f"_DSC{c['photo']} mean ΔE {c['mean_de']:.3f}" for c in verified)
            page += ".\n\n"
        page += "Photos © Zhou Bowei. [Project test/comparison permission only](../../samples/LICENSE.md); other uses require permission.\n"
        (pages / f"{recipe}.md").write_text(page, encoding="utf-8")
    (DOCS / "RECIPES.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Wrote catalog for {len(rows)} recipes ({version}).")


if __name__ == "__main__":
    main()
