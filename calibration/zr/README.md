# Nikon ZR calibration kit

The Nikon ZR version of the [Z 8 calibration kit](../z8/), used to fit the ZR pack of release 1.1. Use it like the other kits ([Convert your own recipe](../../docs/en/convert-your-own-recipe.md)), with `--camera zr` for `scripts/build_release_profiles.py` or `--camera "Nikon ZR"` for `fit`.

| File | Contents |
|---|---|
| `chart.json` | Patch positions, for `nikon-recipes-lr sample` (the same layout as the Z6III kit) |
| `camera-flexible-color.npy` | The chart as Camera Raw renders it with Camera Flexible Color on the ZR |
| `adobe-standard.npy` | The same with Adobe Standard |

How it was made. Every ZR sample we could find is a High Efficiency★ NEF. NX Studio renders a chart written into such a file, but Camera Raw does not open it, so the two halves were measured differently:

- **NX Studio**: the chart was written into a ZR NEF (ISO 100) with [`scripts/make_chart.py`](../../scripts/make_chart.py), and its white balance coefficients were set to those of the Z6III kit's chart, so that both kits describe the same light.
- **Camera Raw**: the ZR and the Z6III share the same sensor, and Adobe's profiles for the two cameras are identical (color matrices, tables and tone curve) except that Camera Flexible Color is 0.10 EV brighter on the ZR. The Camera Raw measurements are therefore the Z6III chart rendered with Camera Flexible Color at +0.10 exposure; Adobe Standard has no such offset and is the Z6III measurement.

The chart RAW is not included because the ZR sample it was made from may not be redistributed. With a lossless NEF of your own ZR, `make_chart.py build` and `align` make the chart and check its alignment.
