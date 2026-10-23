# Nikon Z 8 calibration kit

Everything needed to turn a Nikon Picture Control or Imaging Recipe (`.NP3`) into a Lightroom profile the same way the released profiles are made, with only NX Studio and this project's Python tool. Step-by-step guide: [Convert your own recipe](../../docs/en/convert-your-own-recipe.md) ([中文](../../docs/zh/convert-your-own-recipe.md) · [日本語](../../docs/ja/convert-your-own-recipe.md)).

| File | Contents |
|---|---|
| `chart.NEF.zip` | `chart.NEF`, a Z 8 RAW file with 24,720 color patches (the chart used for every release). Unzip it before use. |
| `chart.json` | Patch positions, for `nikon-recipes-lr sample` |
| `nx-template.nksc` | NX Studio settings for the chart, for `nikon-recipes-lr prepare-nx` |
| `camera-flexible-color.npy` | The chart rendered by Camera Raw with Camera Flexible Color and measured with `nikon-recipes-lr sample`; use with `fit --base "Camera Flexible Color"` (the 1.0 method) |
| `splits.npz` | The fixed training, validation and test patches used for the releases; `scripts/build_release_profiles.py` fits on `train` and reports `test` |
| `adobe-standard.npy` | The same with Adobe Standard; use with the default `fit --base "Adobe Standard"` (the 0.2 method, for profiles that work with any camera) |

The chart's image data is synthetic; its metadata and embedded previews come from the sample photograph `_DSC2849.NEF`, so the [sample photo terms](../../samples/LICENSE.md) apply to the file. Profiles you make with it are yours to use and share.

How the kit was checked (October 2026): the chart renders in NX Studio and Camera Raw within 0.01 ΔE on average of the private chart used before; refitting a released recipe with the kit differs from the published table by about 0.1 ΔE on average. Active D-Lighting, vignette control, distortion control and diffraction compensation are switched off in the chart so that every patch is rendered alike.
