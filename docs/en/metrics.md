# What the scores mean

[中文](../zh/metrics.md) · [日本語](../ja/metrics.md)

The [gallery](https://nikon-recipes-to-lr-profiles.pages.dev/) and the [recipe catalog](../RECIPES.md) show two scores for every profile. Both are measured on the profile file that is actually released, at 100% Amount.

## Difference from NX Studio

The average color difference between the profile and NX Studio over the patches of the test chart, in CIEDE2000 ΔE. A ΔE of about 1 is roughly the smallest difference most people notice side by side. The gallery labels the score *near-identical* below 0.5, *very close* from 0.5 to 1 and *slight difference* from 1. In release 1.0, 223 of 236 recipes are below 1.

What it does not say: it is an average, so single colors can differ more (the catalog also lists the 95th percentile), and it is measured on a chart, not on photographs. A slight tint over a large sky can be more visible than a larger difference inside fine texture, so look at the photographs as well.

Details for contributors: colors are compared in D65 Lab converted from encoded Adobe RGB (1998), with kL = kC = kH = 1. Patches where any input or NX channel is below 0.0005 or above 0.999 are left out, because clipped colors carry no information; `sample_count` is the number used. `fit.heldout` is the same score on a fixed set of patches that was not used for fitting. Three recipes (LeicaSTD, At Dusk, Blue Hour) use NX Studio references rendered with detail settings switched off; the others were rendered with the recipe's own detail settings, which mainly affects highlights.

## Banding risk

How abruptly the color table changes direction. Lightroom interpolates between the table's points, so the result is continuous, but its slope can change from one cell to the next; a sharp change of slope can show as a contour in a smooth sky or in bokeh. The score is the 99th percentile of these changes over all 351,726 faces between the table's cells. The gallery labels it *low* below 0.4, *medium* from 0.4 to 0.6 and *high* from 0.6; in release 1.0 that is 152, 57 and 27 recipes. The bands are fixed values for orientation, not visibility thresholds.

What it does not say: it is not a count of visible bands. A recipe with a strong, intended tonal change (for example high-contrast black and white) scores higher without banding, and a low score does not guarantee a smooth sky in every photo.

Details for contributors: `face_jump_p99`, `face_jump_max` and `face_jump_rms` are the 99th percentile, maximum and RMS of the Frobenius norm of the change in the output-RGB Jacobian across every internal tetrahedral face and every face between neighboring cells, with RGB normalized to 0–1.

## Gallery previews

Each scene is rendered once by Camera Raw from the original RAW file with the base profile, as a 16-bit Adobe RGB image. The render is averaged over 6×6 pixel blocks, the profile's table is applied to every pixel exactly as Lightroom interpolates it, and the result is converted to sRGB and resized to 1280 pixels. NX Studio references are NX Studio JPEG exports, resized the same way. The previews are therefore calculated, not exported from Lightroom; for several recipes they were compared with real Camera Raw renders and matched closely. 8-bit JPEG compression can hide or add very subtle banding, so judge borderline cases on the RAW files in Lightroom.

## Visual reviews

In an October 2026 review of an earlier version (Y7), 58 recipes showed some banding on real photographs. The 0.2 versions of those 58 were checked on several photographs and no banding was seen. Release 1.0 uses the same fitting settings on a different base profile and has lower banding scores for 235 of 236 recipes, but it has not been reviewed photo by photo. Reports of banding are always welcome in the [issues](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose).
