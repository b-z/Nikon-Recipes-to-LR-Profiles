# Release 1.0: profiles on Camera Flexible Color (Y9)

Release 1.0 keeps the fitting method of 0.2 ([Y8](Y8_REBUILD.md): bounded cubic spline, 16 control points per axis, curvature weight 0.001, same training patches and NX Studio references) and changes one input: the chart is rendered by Camera Raw with **Camera Flexible Color** instead of Adobe Standard, and every profile is a Look on that base. This note explains why.

## The problem: darker shadows than NX Studio

Comparing 0.2 previews with NX Studio on the gallery photographs, shadows (L* 10–30) were darker in two of the four scenes for almost every recipe (median −1.3 and −1.6 L*) and slightly more saturated, while the other two scenes showed no offset. Twelve further photographs showed the same split. The difference followed a tight curve against L* and was the same for different recipes, so it was a global tone difference, not a fitting error: the fit itself is unbiased in the shadows on the chart (median within ±0.05 L*).

Tests that ruled out other causes: switching Active D-Lighting off had no effect; NX Studio renders unchanged regions identically when the rest of a RAW is replaced (it maps every pixel the same way); white balance, firmware, lens and Picture Control settings did not separate the two groups of photos.

## The cause: automatic black subtraction in Camera Raw

Camera Raw renders Adobe Standard with an automatic black level (`DefaultBlackRender = Auto`): it estimates flare from the darkest pixels of the photo and subtracts it. Daylight photos without true black get their shadows pulled down; photos that contain black, such as night scenes or our test chart, do not. Experiments on a Z 8 RAW:

- replacing the sky with pure black brightened the untouched shadows by 2.8 L* in Camera Raw and by exactly 0.000 in NX Studio;
- a black patch covering 1% of the frame had the same effect, and a mid-grey sky had almost none;
- with `DefaultBlackRender = None` the effect disappeared.

Every Camera Matching profile Adobe ships for the Z 8 (Camera Flexible Color, Camera Standard, Camera Neutral and others) sets `DefaultBlackRender = None`. Only Adobe Standard uses Auto. NX Studio always uses the sensor's black level.

## The change

On Camera Flexible Color the black-patch test changes nothing (0.000), so the profile no longer depends on the scene. Camera Flexible Color is also Adobe's match of Nikon's Flexible Color Picture Control, on which the Imaging Recipes are built. Adobe's own creative profiles use the same structure: a camera-restricted Look on a Camera Matching base with an RGB table.

Results with the same fitter and the same patches (236 recipes):

| | 0.2 (Adobe Standard) | 1.0 (Camera Flexible Color) |
|---|---:|---:|
| Chart ΔE to NX Studio, median over recipes | 0.70 | 0.51 |
| Recipes closer to NX Studio than 0.2 | | 236 of 236 |
| Banding risk (face-jump p99), median | 0.46 | 0.36 |
| Recipes with a lower banding risk than 0.2 | | 235 of 236 |

On twelve independent photographs (31 photo–recipe combinations, per-pixel tables on full-resolution Camera Raw renders), every combination came closer to NX Studio, for example Filmic 1.10 → 0.68 ΔE and MOSS 0.91 → 0.48 ΔE, and the shadow offset of those recipes fell to within ±0.3 L*. Applying a profile in Camera Raw (base Camera Flexible Color plus the Look at Amount 1.0, 0.5 and 0) matched the numerical prediction within 0.006 ΔE.

## Costs

- Camera Flexible Color exists only for Nikon bodies that support Flexible Color, and the calibration is specific to the Z 8, so 1.0 profiles are restricted to the **Nikon Z 8**. Release 0.2 (Adobe Standard) remains the choice for other cameras.
- At 0% Amount the photo shows Camera Flexible Color rather than Adobe Standard.
- Slightly more chart patches clip in the highlights on this base (2.2% instead of 0.9%); they are left out of the fit as before.

## Reproducing

The [Z 8 calibration kit](../calibration/z8/) contains both Camera Raw baselines. `nikon-recipes-lr fit --base "Camera Flexible Color" --adobe-samples calibration/z8/camera-flexible-color.npy` fits a profile the 1.0 way; see [Convert your own recipe](en/convert-your-own-recipe.md).
