# Changelog

Notable changes to the released profiles and tools. Profile releases are on the [Releases page](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases).

## Unreleased

### Tools
- `fit` uses the smooth spline method of the released profiles by default (`--method spline`, 16 control points, λ 0.001). The previous direct table fit is available as `--method native`.
- `fit` and `export` accept `--group` and `--camera`. Custom profiles go to the `Nikon Recipes LR/Custom` group instead of the 0.1 release group, and their UUID is derived from group and name.
- `--version` option; clearer error messages.

### Project
- Added a Code of Conduct, security policy, changelog, release guide, issue forms and a lint step (ruff) in CI.
- Rewrote the README and contribution guide for community maintenance.
- Website scripts no longer overwrite the release catalog; Y7 gallery data moved from `docs/recipe_metrics.json` to `website/data/y7_metrics.json`.

## 0.2.0 — 2026-10-19

### Profiles
- All 236 recipes now use the **Y8** fit: a bounded C2 cubic spline with 16 control points per axis, sampled to the 32³ table. It gives smoother gradients at some cost in chart accuracy (214 of 236 recipes have a higher chart ΔE than Y7; median 0.47 → 0.70).
- The 58 recipes that still showed banding with Y7 were checked on several photographs with Y8 and no banding was observed. The other 178 were not individually reviewed.
- New group **Nikon Recipes LR 0.2** with new names and UUIDs, so 0.2 can be installed next to 0.1.

### Documentation
- Recipe catalog generated from the release manifest, with Y7 scores for comparison.

## 0.1.0 — 2026-10-08

- First public release: 236 Nikon recipe conversions (19 YC7 + 217 YC4 tables) in the group **Nikon Recipes LR 0.1**.
- Comparison gallery with NX Studio references for all recipes on four photographs.
- Four sample Z 8 RAW files for testing and comparison.
