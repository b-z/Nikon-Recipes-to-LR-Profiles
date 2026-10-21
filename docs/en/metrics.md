# What the scores mean

The recipe catalog reports measurements of the **actual table shipped in each Release profile** (Y8 since 0.2.0), decoded from its XMP, with the previous Y7 scores alongside for comparison. RGBTable evaluation uses native tetrahedral interpolation; a trilinear proxy is not used.

## Fitting error

`fit.mean`, `median` and `p95` are CIEDE2000 between predicted and NX Studio chart samples. Both are encoded Adobe RGB (1998), converted to D65 Lab; kL=kC=kH=1. Samples with any input or target channel below 0.0005 or above 0.999 are excluded. `sample_count` records the number retained.

The primary score is a **current-table chart evaluation**, not independent unseen validation and not a full-photograph score. `fit.heldout` (Y8) and `current_fit_holdout` (Y7) contain the result on the fixed chart test split, excluded from that profile’s fit. Random chart holdout is not equivalent to a new real-world scene.

Three recipes (LeicaSTD, At Dusk and Blue Hour) use the verified detail-off NX chart. The other historical chart exports did not consistently disable detail settings. This is recorded per recipe; treat scores from different measurement policies cautiously. Patch interiors reduce, but do not prove elimination of, local-rendering effects.

CIEDE2000 describes local color differences. It does not model all spatial perception, visual attention or whether a difference looks pleasing. A small neutral tint across a large sky can matter more than a higher local ΔE in texture. Do not choose profiles solely by one average.

## Banding risk

`face_jump_p99`, `face_jump_max` and `face_jump_rms` are the 99th percentile, maximum and RMS of the Frobenius norm of the output-RGB Jacobian change at **every unique internal tetrahedral face and neighboring-cell face**. RGB coordinates are normalized 0–1; slopes are per unit input RGB. A 32³ table has 351,726 evaluated faces.

These are structural scores, not a count of visible bands and not ΔE. Tetrahedral interpolation is continuous, but its derivative is piecewise constant. A large change in slope can reveal contours in smooth skies or bokeh even without a discontinuity in RGB values. Strong legitimate tonal changes can also increase this score; there is no calibrated universal visibility threshold. 8-bit preview quantization, display scaling and JPEG compression introduce additional limitations.

The Y7 fitter directly penalizes mixed changes inside cells and changes across cell faces. Y8 instead fits a bounded C2 cubic tensor spline with 16 control points per axis and a curvature penalty, then samples it into the 32³ table; this removes local waves between chart samples at some cost in chart ΔE. More lattice samples alone do not guarantee smoothness. **Every recipe is audited globally**, independently of the four photographed color paths.

## Photo previews

Four untouched original Z8 samples, published with the photographer's permission, cover bokeh, sky and two landscapes. The default gallery applies the decoded table to area-averaged 16-bit Camera Raw Adobe Standard exports, then converts Adobe RGB to sRGB for display. They are **numerical previews**, not full Lightroom exports; averaging before a nonlinear transform can alter fine-detail colors. Source documentation uses a small example and compact contact sheets; full website images are kept outside Git in a separate asset pack. Resizing can conceal or change visible banding, so use the full gallery or RAWs for that evaluation.

Selected previews are also rendered through actual Camera Raw and compared separately. Their validation report records the sampling and errors; it is not generalized to every profile or Amount. All 236 recipes now have maintainer-exported NX JPEG references on each of the four scenes. The default gallery compares NX with the numerical conversion; either side can also show Adobe Standard. NX JPEGs retain original dimensions in the reference metadata, while web derivatives are downsampled to 768 pixels. JPEG quantization, resizing, and renderer/lens differences prevent these previews from serving as precision fit or banding measurements.

Preview provenance is recorded in [website/data/gallery_manifest.json](../../website/data/gallery_manifest.json); NX reference metadata and the external asset inventory are in the same directory. Use the RAW sample asset and actual Lightroom for a final visual check, especially at 200% Amount. Warning icons reflect the 2026-10-10 maintainer review of Y7: 58 Y7 recipes had residual banding. Those 58 were re-checked with Y8 on multiple photographs and no banding was observed; the other 178 were not individually reviewed with Y8. Neither marked nor unmarked recipes are certified band-free.

For Banding test 2, the Z 14–30mm lens marks distortion correction as mandatory inside the NEF even with Camera Raw’s ordinary lens profile switch off. Website comparisons use an Adobe baseline rendered from a private copy with that correction flag disabled and vignetting control off, matching the uncorrected NX references. Original published NEFs and NX JPEGs are unchanged. This is a benchmark preparation step, not a modification to the downloadable color profiles.
