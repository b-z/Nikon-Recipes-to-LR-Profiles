# Nikon Recipes to LR Profiles

[![Tests](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/actions/workflows/test.yml/badge.svg)](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/actions/workflows/test.yml)
[![Latest release](https://img.shields.io/github/v/release/b-z/Nikon-Recipes-to-LR-Profiles)](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/b-z)

[中文](docs/zh/README.md) · [日本語](docs/ja/README.md)

### 👉 [Open the online gallery](https://nikon-recipes-to-lr-profiles.pages.dev/): compare all 236 recipes with NX Studio and download the ones you like

[Nikon Imaging Cloud](https://imagingcloud.nikon.com/) offers color recipes created by professional photographers. A recipe only changes the JPEGs your camera records; the RAW file stays as it is. If you edit RAW files, the only official way to use a recipe is Nikon's NX Studio, which does not fit the workflow of many photographers.

This project recreates the recipes in **Lightroom and Photoshop Camera Raw**. Choose a recipe in the Profile Browser and set its strength with the **Amount** slider (0–200%). Exposure, white balance, curves and every other adjustment keep working as usual. The current release contains **236 recipes**, and in our tests most of them reproduce the colors of the original closely.

[![KG200P1 on four test photographs. Top row: NX Studio. Bottom row: Lightroom with the converted profile.](docs/images/kg200p1-comparison.jpg)](https://nikon-recipes-to-lr-profiles.pages.dev/#KG200P1)

*The KG200P1 recipe on four test photographs. Top: NX Studio. Bottom: Lightroom with this project's profile at 100% Amount. [See every recipe this way in the gallery](https://nikon-recipes-to-lr-profiles.pages.dev/).*

## Why use it

- **Adjustable strength.** The Amount slider goes from 0 to 200%, and the recipe sits underneath your own edits instead of replacing them: exposure, white balance, curves, masks and presets work as usual.
- **Cameras the official recipes do not support.** Imaging Recipes only work on recent Nikon bodies with the Flexible Color Picture Control, and older bodies cannot use them even in NX Studio. The Adobe pack works with any RAW file Lightroom opens: older Nikons, and other brands too.
- **Measured on each camera.** For the Z 8, Z 9, Z f, Z6III, Z5II and Z50II, every recipe is measured on that body's own RAW data, so the profile follows how NX Studio renders that camera.
- **Any photo you already have.** A recipe can be applied to RAW files shot without it, years ago, or before the recipe existed, and the tool can apply the recipe a photo was shot with automatically.
- **Measured, not eyeballed, and open.** Every recipe has a published difference from NX Studio and a banding-risk score, the gallery compares each one on four photographs, and the tools to convert your own recipe are in this repository.

## Install

1. Download the ZIP for your camera from the [latest release](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest) and unzip it: `…-z8`, `-z9`, `-zf`, `-z6iii`, `-z5ii`, `-z50ii` or `-zr` for Nikon bodies with Camera Flexible Color, `…-adobe` for any other camera. If you only want a few recipes, download them one by one from the [gallery](https://nikon-recipes-to-lr-profiles.pages.dev/) instead.
2. In Lightroom or Camera Raw, open the Profile Browser, choose **Import Profiles** and select the `.xmp` files. Restart Lightroom if they do not appear.
3. Open the **Nikon Recipes LR 1.1** group, pick a recipe and adjust its strength with **Amount**: 100% gives the colors of the original recipe; 30–50% gives a subtle result.

The camera packs are built on Camera Flexible Color and come closest to NX Studio; the Adobe pack is built on Adobe Standard and works with any camera. Each camera pack has color tables measured on that camera. More in [INSTALL](docs/en/INSTALL.md).

## What a profile includes

A profile reproduces the **color and tone** of a recipe: its colors, contrast and tone curve, saturation and color grading, as NX Studio renders them. The recipe's **sharpening, mid-range sharpening and clarity are not included**; those detail settings are ignored, and your own Lightroom settings for sharpening, texture, clarity, noise reduction, grain, vignetting and lens corrections apply as usual.

## Open photos with the recipe you shot with

The camera stores the name of the recipe in every NEF. This project's command-line tool reads it and writes a sidecar next to each RAW, so Lightroom Classic and Camera Raw open the photo with the matching profile already applied:

```sh
nikon-recipes-lr sidecars --profiles /path/to/nikon-recipes-lr-profiles-1.1.0-z8/profiles /path/to/photos
```

Run it before importing the photos. Setup and details: [Apply profiles automatically](docs/en/auto-apply.md).

## Compare the recipes

- **[Online gallery](https://nikon-recipes-to-lr-profiles.pages.dev/)**: every recipe on four photographs, NX Studio against the Lightroom profile, with a blink comparison, two scores and a download button for each recipe.
- **[Recipe catalog](docs/RECIPES.md)**: the creator, the difference from NX Studio and the banding-risk score of every profile ([what the scores mean](docs/en/metrics.md)).

## How it works

### Measuring a recipe

NX Studio is the reference, because it is how Nikon itself applies a recipe to RAW files. For every recipe, NX Studio renders a synthetic test chart: a Z 8 RAW file containing 24,720 color patches that cover dark to bright, neutral to strongly saturated colors in every hue. Camera Raw renders the same chart with the base profile and no recipe. Each patch then gives one pair of colors: what Lightroom starts from, and what the recipe turns it into. The recipe's settings are never translated one by one, because Nikon's curves, Color Blender and Color Grading do not work in the same color space or order as Lightroom's sliders; the profile follows what NX Studio actually produces.

### Fitting a smooth color mapping

From the 24,720 pairs we fit a function that maps any Lightroom color to the recipe's color. A Lightroom color table has 32 points along each of its three axes, almost 33,000 points with three values each, and Lightroom interpolates in straight lines between them. If every point were fitted freely, the table would follow the small measurement noise of each patch and bend slightly differently from cell to cell. In a photo those bends show up where colors change slowly, in skies, skin and out-of-focus backgrounds, as visible steps (banding). Earlier versions of this project showed exactly that.

Since 0.2 the mapping is a **smooth cubic spline** with 16 control points per axis and a curvature penalty: its first and second derivatives are continuous everywhere, so gradients stay smooth, and its coefficients are bounded so that every output stays inside the color space without clipping. The 32³ table is then sampled from this smooth function. The price is a slightly larger difference on the chart; for 1.0 the median difference to NX Studio is still about 0.5 ΔE, below what most people can see. [Method notes](docs/Y8_REBUILD.md).

### Storing it as a Lightroom profile

Each recipe becomes one Adobe **enhanced profile**, a small `.xmp` file that Lightroom Classic, Lightroom and Camera Raw import directly, the same format Adobe uses for its own creative profiles. The important fields are:

- `crs:PresetType="Look"`: the file is a profile that sits on top of a base profile.
- `crs:CameraProfile`: the base profile, `Camera Flexible Color` in the camera packs, `Adobe Standard` in the Adobe pack. Camera Raw renders the RAW with this base first.
- `crs:RGBTable` and `crs:Table_<ID>`: the 32×32×32 color table. Its 16-bit values are stored as offsets from "no change", compressed and written as text; the ID is a checksum of the table. Camera Raw applies it to every pixel after the base profile.
- `crs:SupportsAmount="True"` with a maximum of 200% in the table header: this is what gives the profile its **Amount** slider, which blends between the base profile (0%) and the full recipe (100%) or beyond.
- `crs:CameraModelRestriction` (for example `Nikon Z f`), `crs:Group`, `crs:Name` and `crs:UUID`: where and under which name the profile appears. Each release gets new UUIDs, so releases never overwrite each other.

A profile is the only place in Lightroom where a full 3D color table can live. A develop preset could only set sliders such as HSL and curves, which cannot express how a recipe moves every color, and it would overwrite your own slider settings. A camera profile (DCP) has to be made per camera and offers no Amount slider. With an enhanced profile, the recipe is one choice in the Profile Browser, its strength is adjustable, and every other slider remains yours.

### Why Camera Flexible Color

Up to 0.2 the profiles were built on Adobe Standard. Camera Raw lowers the black level of Adobe Standard depending on the darkest pixels in each photo, so in daylight scenes without true black the shadows came out darker and more saturated than in NX Studio. Camera Flexible Color, Adobe's profile matching Nikon's Flexible Color Picture Control that the recipes are built on, keeps the sensor's black level. With it, 1.0 is closer to NX Studio than 0.2 for all 236 recipes on the chart, shadows in real photos come much closer to NX Studio, and the banding-risk score is lower for 235 of them. [Details](docs/Y9_FLEX_BASE.md).

All of Adobe's Camera Matching profiles (Camera Standard, Camera Neutral and so on) keep the sensor's black level, so any of them would fix the shadows. Camera Flexible Color is the one that matches the starting point of the recipes: Imaging Recipes are made on top of Nikon's Flexible Color Picture Control. Starting from Adobe's match of it, the color table only has to describe what the recipe itself changes, which is the smallest and therefore smoothest correction. Adobe makes Camera Flexible Color for each Nikon body that has Flexible Color (Z 8, Z 9, Z f, Z6III, Z5II, Z50II, ZR). Its brightness does not land exactly where NX Studio puts it on every body, so since 1.1 each body's tables are fitted on a chart made from that body's own RAW data, with the same method and the same patches as the Z 8. [Details](docs/Y9_FLEX_BASE.md#one-table-per-camera).

## Convert your own recipe

Picture Controls you made yourself, or recipes that are not in the release, can be converted too. The repository contains a [Z 8 calibration kit](calibration/z8/) with the chart, the NX Studio settings and the Camera Raw measurements; with NX Studio and Python a recipe takes a few minutes. See [Convert your own recipe](docs/en/convert-your-own-recipe.md).

## Known limitations

- **Banding.** Smooth skies and bokeh can still show steps, especially at high Amount. Please [report](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose) any you find, with the recipe and a small crop.
- **Approximation.** For 223 of the 236 recipes the average chart difference to NX Studio is below 1 ΔE (CIEDE2000), roughly the smallest difference people notice; the largest is 1.44 ΔE. Single colors and photos can differ more.

## Contributing

Contributions are welcome: calibrations for other Nikon bodies, banding reports with reproducible examples, better fitting methods, tests, documentation and translations. Start with [CONTRIBUTING](CONTRIBUTING.md); everyone taking part is expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Changes between releases are listed in the [CHANGELOG](CHANGELOG.md).

## Support the project

The project is maintained in spare time. If the profiles are useful to you, you can support it through [GitHub Sponsors](https://github.com/sponsors/b-z) or with WeChat. Sponsoring is entirely optional and does not affect how issues or pull requests are handled.

<table><tr>
<td align="center" valign="middle"><a href="https://github.com/sponsors/b-z"><img src="https://img.shields.io/badge/GitHub%20Sponsors-%E2%9D%A4%20Sponsor-db61a2?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Sponsor on GitHub" height="36"></a></td>
<td align="center" valign="middle"><img src="docs/images/wechat-reward.jpg" alt="WeChat reward QR code" width="180"></td>
</tr></table>

## Credits and licenses

- Recipes belong to their creators, who are credited in every profile, in the catalog and in the [gallery](https://nikon-recipes-to-lr-profiles.pages.dev/). Original NP3 files are not redistributed; get them from the creators, Nikon Imaging Cloud or the [Nikon-Recipes archive](https://github.com/shouryan01/Nikon-Recipes).
- Code and documentation: [MIT](LICENSE). Generated profiles: MIT with the attribution notes in [PROFILE_LICENSE](PROFILE_LICENSE.md). Third-party notes: [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md).
- The four sample photographs, the calibration chart (whose embedded previews come from one of them) and images made from them are **not** MIT-licensed. They may be used only for testing and comparing this project; see [samples/LICENSE.md](samples/LICENSE.md).

This is an independent community project, not affiliated with or endorsed by Nikon or Adobe.
