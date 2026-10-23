# Nikon Z f calibration kit

The Nikon Z f version of the [Z 8 calibration kit](../z8/): the same 24,720 patches, written into a Nikon Z f RAW file so that NX Studio and Camera Raw render them as this camera. Release 1.1 fits the Nikon Z f pack on this kit. Use it like the Z 8 kit ([Convert your own recipe](../../docs/en/convert-your-own-recipe.md)), with `--camera zf` for `scripts/build_release_profiles.py` or `--camera "Nikon Z f"` for `fit`; the NX Studio template and the training patches are those of the Z 8 kit.

| File | Contents |
|---|---|
| `chart.NEF.zip` | `chart.NEF`, a Nikon Z f RAW file with the 24,720 color patches. Unzip it before use. Its metadata and embedded previews come from a CC0 sample from [raw.pixls.us](https://raw.pixls.us/). |
| `chart.json` | Patch positions, for `nikon-recipes-lr sample` |
| `camera-flexible-color.npy` | The chart rendered by Camera Raw with Camera Flexible Color and measured with `nikon-recipes-lr sample` |
| `adobe-standard.npy` | The same with Adobe Standard |

The kit was made with [`scripts/make_chart.py`](../../scripts/make_chart.py). Active D-Lighting, vignette control, distortion control and diffraction compensation are switched off in the chart.
