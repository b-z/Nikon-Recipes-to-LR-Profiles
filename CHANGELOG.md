# Changelog

Notable changes to the released profiles and tools. Profile releases are on the [Releases page](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases).

## 1.0.1 — 2026-10-23

### Profiles
- **One pack per camera.** The 1.0 tables now come in a pack for every Nikon body that has a Camera Flexible Color profile in Lightroom: Z 8, Z 9, Z f, Z6III, Z5II, Z50II and ZR. A profile can be restricted to only one camera model, so each pack has its own restriction and UUIDs; the tables are the same. The Z 8 pack is identical to 1.0.0. On sample RAW files from a Z f and a Z6III the camera packs were closer to NX Studio than the Adobe pack.
- **Adobe pack** for every other camera: the Y8 tables on Adobe Standard without a camera restriction, in the group **Nikon Recipes LR 1.0 Adobe**.
- No checksum file; each ZIP has its own README and manifest.

### Website and tools
- "Download this recipe" and the download dialog ask for the camera and download the matching profile or pack.
- `scripts/package_release.py` builds all packs; `src/nikon_recipes_lr/cameras.py` defines them.

## 1.0.0 — 2026-10-22

### Profiles
- All 236 profiles are now built on **Camera Flexible Color** instead of Adobe Standard (internally "Y9"), with the same fitting settings as 0.2. Camera Raw lowers the black level of Adobe Standard depending on the darkest pixels of each photo, which made shadows in daylight photos darker and more saturated than in NX Studio; Camera Flexible Color keeps the sensor's black level. All 236 recipes are closer to NX Studio on the chart (median 0.70 → 0.51 ΔE) and 235 have a lower banding-risk score (median 0.46 → 0.36). [Details](docs/Y9_FLEX_BASE.md).
- The profiles are limited to the **Nikon Z 8**, because the base profile and the calibration are specific to it. Release 0.2.0 remains available for other cameras.
- New group **Nikon Recipes LR 1.0** with new names and UUIDs, so 1.0 can be installed next to 0.2.
- The release ZIP contains a README with installation and usage steps in English, Chinese and Japanese.

### Tools
- New `sidecars` command: reads the Picture Control name each NEF records and writes an XMP sidecar that applies the matching profile when the photo is imported into Lightroom Classic or opened in Camera Raw.
- `fit`, `export` and `render` accept `--base` (`Adobe Standard` or `Camera Flexible Color`).
- `fit` uses the smooth spline method of the released profiles by default (`--method spline`, 16 control points, λ 0.001). The previous direct table fit is available as `--method native`.
- `fit` and `export` accept `--group` and `--camera`. Custom profiles go to the `Nikon Recipes LR/Custom` group, and their UUID is derived from group and name.
- `--version` option; clearer error messages.

### Calibration kit and documentation
- The repository now contains a [Z 8 calibration kit](calibration/z8/) (chart, NX Studio settings and Camera Raw measurements for both base profiles), so recipes can be converted with NX Studio and Python alone: [Convert your own recipe](docs/en/convert-your-own-recipe.md). The chart is the one used for every release, now in a file whose metadata and previews come from a published sample photograph.
- New guides: [Apply profiles automatically](docs/en/auto-apply.md), adding new recipes (in the releasing guide), and a rewritten explanation of [the scores](docs/en/metrics.md).
- README, catalog and guides rewritten for photographers, in English, Chinese and Japanese.
- Added a Code of Conduct, security policy, changelog, release guide, issue forms and a lint step (ruff) in CI.

### Website
- Redesigned gallery in English, Chinese and Japanese: help and download dialogs, recipes listed by folder, all previews at 1280 px through the same steps, per-recipe downloads of the release profiles (1.0 and 0.2), and a mobile layout.
- New build scripts `website/scripts/make_previews.py` and `build_site.py`; the earlier ingest and gallery scripts and the Y7 gallery data were removed.
- Releases attach only the profiles ZIP and checksums; the sample RAWs stay on the v0.1.0 release.

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
