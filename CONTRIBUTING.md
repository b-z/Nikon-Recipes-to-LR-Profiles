# Contributing

Thank you for helping. This project is maintained by volunteers. Issues and pull requests in English are preferred so that everyone can follow them, but reports in Chinese or Japanese are welcome too ([中文](docs/zh/CONTRIBUTING.md) · [日本語](docs/ja/CONTRIBUTING.md)).

By taking part you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help

- **Report banding or color problems** with the [issue form](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose). The most useful reports name the recipe, release, Amount, camera and Lightroom version, and include a small crop you are allowed to share.
- **Calibrate other cameras.** Only the Nikon Z 8 is calibrated. Chart renders from other bodies are the most valuable data contribution; see the [calibration guide](docs/en/calibration.md).
- **Convert new recipes.** The [Z 8 calibration kit](calibration/z8/) makes this possible with NX Studio and Python alone ([guide](docs/en/convert-your-own-recipe.md)); open an issue with the recipe and its creator before sending profiles.
- **Improve fitting.** Smoother or more accurate fits, better banding metrics and perceptual evaluation.
- **Code and tooling.** Portability (Windows/Linux rendering paths), tests, the gallery website.
- **Documentation and translations.** English is the primary language; Chinese and Japanese pages are kept in sync for user-facing docs.

For anything larger than a small fix, please open an issue first so the approach can be discussed before you spend time on it.

## Development setup

Python 3.10 or newer.

```sh
git clone https://github.com/b-z/Nikon-Recipes-to-LR-Profiles.git
cd Nikon-Recipes-to-LR-Profiles
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Before sending a pull request, run what CI runs:

```sh
ruff format src tests scripts website/scripts
ruff check src tests scripts website/scripts
python -m pytest
```

The core library and CLI need only Python. Rendering (`nikon-recipes-lr render`) needs macOS, Adobe Photoshop and ExifTool; making charts (`make-target`) and writing import sidecars (`sidecars`) need ExifTool. NX Studio is used manually.

## Project layout

| Path | Contents |
|---|---|
| `src/nikon_recipes_lr/` | Library and CLI: NP3 reader, chart generator, sampling, fitters (`spline.py` for released profiles, `fit.py` for the direct table fit), RGBTable/XMP codec, tetrahedral interpolation, banding audit, and import sidecars (`sidecar.py`, with the recipe-to-Picture-Control table `picture_controls.json`) |
| `tests/` | Unit and CLI tests (no vendor software needed) |
| `scripts/` | Maintainer scripts: `write_catalog.py` (recipe catalog from the release manifest), `package_release.py` (release ZIP), `write_picture_controls.py` (Picture Control names for `sidecars`) |
| `docs/` | User documentation, recipe catalog and method notes; `docs/release_manifest.json` describes the current release |
| `calibration/` | Calibration kits: chart RAW, patch positions, NX Studio settings and Camera Raw measurements per camera |
| `website/` | Gallery page, data and build scripts; the image library is kept outside Git ([website/README.md](website/README.md)) |
| `examples/` | Small synthetic chart data for trying the CLI |
| `samples/` | Notes and license for the four sample photographs (the RAWs are an asset of the v0.1.0 release) |

## Pull request guidelines

- Keep each pull request focused on one change, and add or update tests for changed behavior.
- **Color and banding changes need evidence.** State which data were used for fitting and which for evaluation; a chart ΔE improvement or a single photo is not enough to claim a banding fix. Keep the full-table `audit` results in your description, and say whether anything was checked in Lightroom or Camera Raw.
- Changes to profiles in a release go through the release manifest and catalog (see [RELEASING](docs/RELEASING.md)); do not edit `docs/recipes/*.md` by hand, regenerate them with `python scripts/write_catalog.py`.
- Use explicit input and output paths; do not add machine-specific default paths.
- Large data (RAW files, full-size images, render outputs) does not belong in Git history. The calibration kits are the exception: they are small once zipped and needed to use the tools.

## What cannot be accepted

- Original NP3 recipe collections, Adobe SDK source, Adobe base profiles (DCP) or other vendor files.
- Photos or data you do not have the right to share under the project's licenses.
- Fuji film simulation conversions (out of scope for now).

## Licensing of contributions

Contributions are accepted under the [MIT license](LICENSE) of the project. No separate contributor agreement is required. Sample photographs follow their own [terms](samples/LICENSE.md).
