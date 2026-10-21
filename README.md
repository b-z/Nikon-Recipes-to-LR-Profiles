# Nikon Recipes to LR Profiles

[![Tests](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/actions/workflows/test.yml/badge.svg)](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/actions/workflows/test.yml)
[![Latest release](https://img.shields.io/github/v/release/b-z/Nikon-Recipes-to-LR-Profiles)](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[中文](docs/zh/README.md) · [日本語](docs/ja/README.md)

Use the looks from Nikon Imaging Cloud **Imaging Recipes** in Lightroom and Adobe Camera Raw, with an **Amount slider from 0 to 200%**. Exposure, white balance and all other RAW edits stay available.

The current release contains **236 recipe conversions** as enhanced-profile `.xmp` files built on Adobe Standard. No DCP or installer is needed. Each profile is calibrated against NX Studio renders, so it is a close approximation of the recipe, not Nikon's renderer and not a slider-by-slider translation of the NP3 file.

![NX Studio (left) and this project's Lightroom conversion (right), Filmic recipe](docs/images/filmic-example.jpg)

## Use the profiles

1. Download `nikon-recipes-lr-profiles-<version>.zip` from the [latest release](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest) and unzip it.
2. In Lightroom or Camera Raw, open the Profile Browser, choose **Import Profiles** and select the `.xmp` files in `profiles/`. Restart Lightroom if they do not appear.
3. Open the **Nikon Recipes LR 0.2** group, pick a look and adjust **Amount**. 30–50% gives a subtle result.

Profiles from a new release have their own group and IDs, so they can be installed next to an older release. Delete the old group when you no longer need it. See [INSTALL](docs/en/INSTALL.md) for details.

## Compare the recipes

- **[Interactive gallery](https://nikon-recipes-to-lr-profiles.pages.dev/)**: every recipe on four photographs, NX Studio next to the Lightroom conversion, with A/B blinking and per-recipe downloads.
- **[Recipe catalog](docs/RECIPES.md)**: author credit, fitting error and banding-risk score for each profile ([what the scores mean](docs/en/metrics.md)); machine-readable as [`docs/release_manifest.json`](docs/release_manifest.json).

## How it works

1. A synthetic chart RAW with about 24,000 color patches is rendered twice: once by NX Studio with the recipe applied, and once by Camera Raw with Adobe Standard.
2. A smooth, bounded 3D color mapping is fitted from the Adobe colors to the NX colors. Since 0.2.0 this is a cubic spline with 16 control points per axis ([method notes](docs/Y8_REBUILD.md)), which gives smoother gradients than fitting the table directly.
3. The mapping is stored as a 32³ RGB table inside a Lightroom "Look" profile on top of Adobe Standard. Lightroom's Amount slider blends it with the original.

The NP3 file supplies the recipe's name and metadata. The colors themselves come from the NX Studio renders.

## Known limitations

- **Banding.** Smooth skies and bokeh can still show steps, especially at high Amount. The 58 recipes that showed banding in the previous version were re-checked on several photographs with no banding seen; the other 178 have not been individually reviewed. Please [report](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose) any you find.
- **Camera.** Only the Nikon Z 8 has been calibrated and tested. Other bodies may look different.
- **Scope.** The profiles reproduce color and global tone. Sharpening, clarity, grain, vignetting and lens corrections are left to your own Lightroom settings.
- **Approximation.** The mean chart difference to NX Studio is below 1 ΔE (CIEDE2000) for 197 of 236 recipes and at most 1.85 ΔE. Individual colors and photos can differ more.

## Calibrate a recipe yourself

```sh
python -m pip install -e .
nikon-recipes-lr fit --adobe-samples adobe.json --nx-samples nx.json \
  --name "My recipe" --author "Recipe author" --output my-recipe.xmp --report my-recipe-report.json
nikon-recipes-lr audit my-recipe.xmp
```

New recipes need matching NX Studio and Camera Raw renders of the chart. The [calibration guide](docs/en/calibration.md) covers chart generation, NX batch export, sampling and fitting. [`examples/`](examples/README.md) has a small synthetic data set that runs without any Nikon or Adobe software.

## Contributing

Contributions are welcome, especially calibrations for other Nikon bodies, banding reports with reproducible examples, smoother fitting methods, tests and translations. Start with [CONTRIBUTING](CONTRIBUTING.md); all participants are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Release history is in the [CHANGELOG](CHANGELOG.md).

## Support

If the profiles are useful to you, you can support the project through [GitHub Sponsors](https://github.com/sponsors/b-z). Sponsorship is entirely optional and does not affect how issues or pull requests are handled.

## Credits and licenses

- Recipes belong to their creators, who are credited in every profile and in the catalog. Original NP3 files are not redistributed; get them from the creators, Nikon Imaging Cloud or the [Nikon-Recipes archive](https://github.com/shouryan01/Nikon-Recipes).
- Code and documentation: [MIT](LICENSE). Generated profiles: MIT with the attribution notes in [PROFILE_LICENSE](PROFILE_LICENSE.md). Third-party notes: [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md).
- The four sample photographs and images derived from them are **not** MIT-licensed. They may be used only for testing and comparing this project; see [samples/LICENSE.md](samples/LICENSE.md).

This is an independent community project, not affiliated with or endorsed by Nikon or Adobe.
