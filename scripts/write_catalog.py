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
DOCS = ROOT/'docs'
GALLERY = 'https://nikon-recipes-to-lr-profiles.pages.dev/docs/gallery'


def main():
    rows = json.loads((DOCS/'release_manifest.json').read_text(encoding='utf-8'))
    version = __version__
    checks = {}
    for name in ('acr_validation.json', 'y8_acr_validation.json'):
        for check in json.loads((DOCS/name).read_text(encoding='utf-8')):
            checks.setdefault((check['recipe'], check['table_id']), []).append(check)
    flagged = sum(row['prior_y7_banding'] for row in rows)
    index = [f'# Recipe catalog — {version}', '',
             f'{len(rows)} Nikon conversions, all **Y8** (smooth spline fit sampled to a 32³ RGB table). '
             '**Banding is a known issue**; scores are not universal visibility thresholds. '
             '[Definitions](en/metrics.md) · [Y8 method and review](Y8_REBUILD.md) · [Online gallery](https://nikon-recipes-to-lr-profiles.pages.dev/)', '',
             'Chart ΔE is current-table evaluation on existing targets. Face p99 measures native RGB slope change globally; it is not ΔE. '
             f'Y7 columns are the previous conversion, for comparison only. Reviewed: the {flagged} recipes that showed residual banding with Y7 '
             'were checked by the owner with Y8 on multiple photographs and no banding was observed. '
             f'The other {len(rows)-flagged} were not individually reviewed with Y8.', '',
             '| Recipe / original author | Chart mean ΔE | Chart p95 | Face p99 | Y7 mean ΔE | Y7 face p99 | Reviewed with Y8 |',
             '|---|---:|---:|---:|---:|---:|:---:|']
    pages = DOCS/'recipes'
    pages.mkdir(exist_ok=True)
    for row in rows:
        recipe = row['recipe']; fit = row['fit']; risk = row['banding']; old = row['previous']
        author = html.escape(row['author']); display = html.escape(row['display'])
        reviewed = '✓' if row['prior_y7_banding'] else ''
        index.append(f'| [{display} — {author}](recipes/{quote(recipe, safe="")}.md) | {fit["mean"]:.3f} | {fit["p95"]:.3f} | '
                     f'{risk["face_jump_p99"]:.3f} | {old["fit_mean"]:.3f} | {old["face_jump_p99"]:.3f} | {reviewed} |')
        page = f'''# {display}

Original author: **{author}**. [NP3 archive]({row['input_recipe_source']}) · [All recipes](../RECIPES.md)

Profile: `{row['file']}` (Release {version}) · Conversion: **{row['source_version']}** · Amount: **100%**.

| Measurement | Y8 (shipped) | Y7 (previous) |
|---|---:|---:|
| Chart mean ΔE | {fit['mean']:.4f} | {old['fit_mean']:.4f} |
| Chart median ΔE | {fit['median']:.4f} | — |
| Chart p95 ΔE | {fit['p95']:.4f} | {old['fit_p95']:.4f} |
| Chart held-out mean ΔE | {fit['heldout']['mean']:.4f} | — |
| Native face jump p99 | {risk['face_jump_p99']:.4f} | {old['face_jump_p99']:.4f} |
| Native face jump maximum / RMS | {risk['face_jump_max']:.4f} / {risk['face_jump_rms']:.4f} | — |
| Valid chart samples | {fit['sample_count']} | |

Review: **{row['owner_review']}** NX target: {row['measurement_policy']}.

[Score definitions and limitations](../en/metrics.md). These are current-table chart scores and global structural banding-risk scores, not a visible-band pass/fail verdict. A low average ΔE does not guarantee smooth skies or bokeh.

## Visual comparisons

[View this recipe on all four scenes]({GALLERY}#{quote(recipe, safe="")}). [Small NX/LR contact sheets](../comparisons/README.md) (made with the previous Y7 tables).

'''
        verified = checks.get((recipe, row['source_table_id']), [])
        if verified:
            page += '## Actual Camera Raw verification\n\nThe shipped Y8 table was rendered through actual Camera Raw and compared with the numerical preview: '
            page += ', '.join(f'_DSC{c["photo"]} mean ΔE {c["mean_de"]:.3f}' for c in verified)
            page += '. [All checks](../y8_acr_validation.json).\n\n'
        page += 'Photos © b-z / Zhou Bowei. [Project test/comparison permission only](../../samples/LICENSE.md); other uses require permission.\n'
        (pages/f'{recipe}.md').write_text(page, encoding='utf-8')
    (DOCS/'RECIPES.md').write_text('\n'.join(index)+'\n', encoding='utf-8')
    print(f'Wrote catalog for {len(rows)} recipes ({version}).')


if __name__ == '__main__':
    main()
