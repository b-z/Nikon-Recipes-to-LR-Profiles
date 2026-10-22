# Comparison gallery

[Online gallery](https://nikon-recipes-to-lr-profiles.pages.dev/) · [Website source, build and deployment](../website/README.md)

The gallery shows every recipe on four photographs: two landscapes, out-of-focus transitions and a smooth sky. Any two of NX Studio, the 1.0 profile, the 0.2 profile and the two base profiles can be compared by blinking or with a slider. All profiles are shown at 100% Amount. How the previews are calculated, and what they can and cannot show, is explained in [what the scores mean](en/metrics.md#gallery-previews).

## Prepare NX Studio references

The NX Studio images are the reference the profiles are compared with, so they must show exactly the recipe and nothing else.

- Use copies of the **untouched original RAWs** (the sample RAWs on the v0.1.0 release), one copy per recipe, each with an NX Studio sidecar that applies the recipe. Metadata-sanitized copies of the same RAWs rendered abnormal colors with recipe sidecars in NX Studio, although their image data was unchanged; the cause is not known.
- Keep as-shot white balance and zero exposure compensation. Switch Active D-Lighting explicitly **off** (not "same as camera"), turn off optional optical corrections, and switch off detail processing such as sharpening and clarity, which the profiles do not reproduce.
- Check in NX Studio that the recipe name and settings were applied before exporting a batch; a sidecar that parses correctly does not prove NX Studio used it.
- Export JPEG at maximum quality and original size, converted to sRGB with the ICC profile embedded, and without output sharpening. Name each file `<scene>_<recipe>.jpg`. [NX Studio export help](https://nikonimglib.com/nxstdo/onlinehelp/en/saving_pictures_in_other_formats_64.html).

JPEG is fine for browsing. Use 16-bit TIFF for fitting and for precise banding checks, because JPEG compression and 8-bit values can add or hide faint bands.
