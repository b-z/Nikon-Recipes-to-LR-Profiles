# Nikon Z5II calibration kit

The Nikon Z5II version of the [Z 8 calibration kit](../z8/): the same 24,720 patches, written into a Nikon Z5II RAW file so that NX Studio and Camera Raw render them as this camera. Release 1.1 fits the Nikon Z5II pack on this kit. Use it like the Z 8 kit ([Convert your own recipe](../../docs/en/convert-your-own-recipe.md)), with `--camera z5ii` for `scripts/build_release_profiles.py` or `--camera "Nikon Z 5 2"` for `fit`; the NX Studio template and the training patches are those of the Z 8 kit.

| File | Contents |
|---|---|
| `chart.json` | Patch positions, for `nikon-recipes-lr sample` |
| `camera-flexible-color.npy` | The chart rendered by Camera Raw with Camera Flexible Color and measured with `nikon-recipes-lr sample` |
| `adobe-standard.npy` | The same with Adobe Standard |

The chart RAW is not included: it was made from a review sample published by PhotographyBlog, which may not be redistributed. To convert recipes for the Nikon Z5II, make the chart from any lossless or uncompressed NEF of your own Nikon Z5II with `python scripts/make_chart.py build --donor your.NEF --pitch 30 --output calibration/z5ii-own`, then copy this kit's `chart.json` and `.npy` files into that folder (the patch layout is the same for every Nikon Z5II NEF at full size) and check the alignment with `make_chart.py align` on an NX Studio export.

The kit was made with [`scripts/make_chart.py`](../../scripts/make_chart.py). Active D-Lighting, vignette control, distortion control and diffraction compensation are switched off in the chart.
