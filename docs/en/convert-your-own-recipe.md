# Convert your own recipe

[中文](../zh/convert-your-own-recipe.md) · [日本語](../ja/convert-your-own-recipe.md)

Any Picture Control or Imaging Recipe saved as an `.NP3` file can be turned into a Lightroom profile, including ones you made yourself. The tool measures how NX Studio renders a color chart with your recipe and fits a profile to it, the same way the released profiles are made. Once everything is installed, a recipe takes a few minutes.

## What you need

- **Your recipe as an `.NP3` file.** On the camera: *Photo shooting menu › Manage Picture Control › Load/save › Copy to memory card*; the file is written to the card's `NIKON/CUSTOMPC` folder. Recipe creators often share NP3 files directly.
- **[NX Studio](https://imaging.nikon.com/imaging/lineup/software/nx_studio/)**, Nikon's free RAW software for macOS and Windows.
- **Python 3.10 or newer.**
- **This repository**, which contains the tool and the [Z 8 calibration kit](../../calibration/z8/): the chart RAW, the positions of its patches, the NX Studio settings and the matching Camera Raw measurements. You do not need to render anything in Lightroom or Photoshop.

```sh
git clone https://github.com/b-z/Nikon-Recipes-to-LR-Profiles.git
cd Nikon-Recipes-to-LR-Profiles
python -m pip install -e .
unzip calibration/z8/chart.NEF.zip -d calibration/z8
```

The examples below run in the repository folder and assume your recipe is `MyRecipe.NP3`.

## 1. Prepare the chart for NX Studio

```sh
nikon-recipes-lr prepare-nx --source calibration/z8/chart.NEF --template calibration/z8/nx-template.nksc \
  --recipes MyRecipe.NP3 --output nx-batch
```

This creates `nx-batch/MyRecipe.NEF` with NX Studio settings that apply your recipe. You can list several `.NP3` files at once.

## 2. Export the chart from NX Studio

1. Open the `nx-batch` folder in NX Studio and select the chart. The Picture Control in the adjustment panel should show your recipe.
2. Choose **Export**, set the format to **TIFF (16-bit)**, keep the original size, and save `MyRecipe.TIF` next to the NEF. The kit's settings already use the Adobe RGB color space.

The chart looks like rows of colored stripes; the thumbnail may still show the photo the chart file was made from, which can be ignored.

## 3. Measure and fit

```sh
nikon-recipes-lr sample nx-batch/MyRecipe.TIF --metadata calibration/z8/chart.json --output MyRecipe-nx.json
nikon-recipes-lr fit --adobe-samples calibration/z8/camera-flexible-color.npy --base "Camera Flexible Color" \
  --nx-samples MyRecipe-nx.json --name "MyRecipe" --author "Your name" \
  --output MyRecipe.xmp --report MyRecipe-report.json
nikon-recipes-lr audit MyRecipe.xmp
```

- `sample` stops with a message if the TIFF is not 16-bit Adobe RGB at the chart's size.
- `mean_de` in the output is the average difference to NX Studio on the chart. Below 1 is hard to see; the released profiles range from about 0.1 to 1.4.
- `audit` reports the banding-risk score ([what the scores mean](metrics.md)).
- Use the name the camera shows for your Picture Control as `--name` if you want [`sidecars`](auto-apply.md) to apply the profile automatically.

This makes a profile like the camera packs of the release, built on Camera Flexible Color and restricted to the Z 8 (for another body, use its kit; see [below](#other-cameras-and-your-own-chart)). For a profile on Adobe Standard that appears for every camera, like the Adobe pack, use the Adobe Standard measurements and drop the camera restriction:

```sh
nikon-recipes-lr fit --adobe-samples calibration/z8/adobe-standard.npy --camera "" \
  --nx-samples MyRecipe-nx.json --name "MyRecipe" --author "Your name" --output MyRecipe-any-camera.xmp
```

Fitting takes a few seconds. With the kit, a released recipe refitted this way differs from the published profile by about 0.1 ΔE on average.

## 4. Use it in Lightroom

Import `MyRecipe.xmp` through the Profile Browser (**Import Profiles**). It appears in the **NRLR - Custom** group. Check it on photos with smooth skies or bokeh, at 100% and at higher Amount, before relying on it. Like the released profiles, it reproduces color and tone only; the recipe's sharpening, mid-range sharpening and clarity are not included.

## Other cameras and your own chart

The repository has a kit for each body the release is fitted on: [Z 8](../../calibration/z8/), [Z 9](../../calibration/z9/), [Z f](../../calibration/zf/), [Z50II](../../calibration/z50ii/), [Z6III](../../calibration/z6iii/) and [Z5II](../../calibration/z5ii/). Camera Raw and NX Studio do not place every body's brightness in exactly the same way, so for another body use its kit: its `chart.NEF` with `prepare-nx`, its `chart.json` with `sample`, its `camera-flexible-color.npy` with `fit`, and its Camera Raw model name with `--camera` (for example `"Nikon Z f"`; the names are listed in `src/nikon_recipes_lr/cameras.py`). The Z6III and Z5II kits have no chart RAW; their READMEs explain how to make one from your own photo.

For a body without a kit (the ZR, for example), make one with [`scripts/make_chart.py`](../../scripts/make_chart.py) from any lossless or uncompressed NEF of that camera, render the chart once with NX Studio and Camera Raw, and measure the Camera Raw render with `sample`. The [calibration workflow](calibration.md) has the background. Kits for other cameras are very welcome as contributions.
