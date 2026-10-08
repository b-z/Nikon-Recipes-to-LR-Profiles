# Actual Camera Raw preview checks

12 actual renders: LeicaSTD, Bleach Blue and Filmic × four Z8 photographs, at 100% Amount. Camera Raw output metadata was checked against the requested Look name, table fingerprint and UUID. Baseline settings were As Shot WB, Adobe Standard, linear user curve, and zero Basic/detail/lens settings.

Overview pixels were area-averaged by a factor of 6; measurements sampled every fourth overview pixel. Numerical previews apply the table after averaging, while Camera Raw applies it before averaging. This creates larger differences in texture and clipped regions. It does not prove exact equivalence for all recipes or user edits.

| Photo | Recipe | Mean ΔE | p95 ΔE |
|---|---|---:|---:|
| _DSC2694 | BleachBlue_Aparupa | 0.0226 | 0.0760 |
| _DSC2694 | Filmic_Fabio | 0.0348 | 0.1190 |
| _DSC2694 | LeicaSTD | 0.0202 | 0.0674 |
| _DSC2849 | BleachBlue_Aparupa | 0.3292 | 1.3445 |
| _DSC2849 | Filmic_Fabio | 0.3891 | 1.5801 |
| _DSC2849 | LeicaSTD | 0.2013 | 0.7658 |
| _DSC5054 | BleachBlue_Aparupa | 0.0226 | 0.0722 |
| _DSC5054 | Filmic_Fabio | 0.0378 | 0.1204 |
| _DSC5054 | LeicaSTD | 0.0292 | 0.1011 |
| _DSC9046 | BleachBlue_Aparupa | 0.0867 | 0.4066 |
| _DSC9046 | Filmic_Fabio | 0.1137 | 0.4859 |
| _DSC9046 | LeicaSTD | 0.0609 | 0.2518 |

Source: [machine-readable results](../acr_validation.json). Actual ACR images are included on the hosted recipe pages; source documentation links to the online gallery. All 944 owner-produced NX references are available on the website. Photos retain the [restricted project-test terms](../../samples/LICENSE.md).

Banding test 2 was rechecked after disabling the lens’s mandatory distortion flag on a private render copy. The original RAWs and NX references are unchanged; see [measurement definitions](metrics.md).
