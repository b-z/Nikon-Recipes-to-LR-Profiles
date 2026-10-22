# Nikon Recipes to LR Profiles 1.0.0

Lightroom and Camera Raw profiles for 236 Nikon Imaging Cloud recipes. Compare them online and download single recipes at https://nikon-recipes-to-lr-profiles.pages.dev/

## Install

1. Unzip this archive.
2. Open the Profile Browser and import the `.xmp` files in `profiles/`:
   - Lightroom Classic: Develop module, Basic panel, click the four-square icon next to **Profile**, then **+** › **Import Profiles**.
   - Lightroom: **File › Import Profiles & Presets**.
   - Camera Raw: Edit panel, Profile Browser, then the **…** menu › **Import Profiles & Presets**.
3. Restart Lightroom if the profiles do not appear. No installer or separate DCP file is needed.

## Use

1. Open a photo taken with a **Nikon Z 8**. The 1.0 profiles appear only for Z 8 photos (see *Other cameras* below).
2. In the Profile Browser, open a group whose name starts with **Nikon Recipes LR 1.0** (one group per recipe creator) and click a recipe.
3. Set its strength with the **Amount** slider under the profile name: 100% matches the recipe, 30–50% gives a subtle result, up to 200% strengthens it.
4. Edit as usual. Exposure, white balance, curves and every other slider keep working. The profile contains the recipe's color and tone only; its sharpening, mid-range sharpening and clarity are not included.

To open new photos with the recipe they were shot with, see https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/blob/main/docs/en/auto-apply.md

## Other cameras

Version 1.0 is built on Camera Flexible Color, Adobe's match of Nikon's Flexible Color Picture Control, and is limited to the Nikon Z 8. For other cameras use version 0.2 (built on Adobe Standard, works with any camera): https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/tag/v0.2.0 . Both versions have their own groups and can be installed side by side.

## Good to know

- Banding can still appear in smooth skies and bokeh, especially at high Amount. Please report cases at https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues
- `manifest.json` lists every profile with its creator and scores.
- Recipes belong to their creators, who are credited in each profile. Original NP3 files are not included. The profiles are MIT-licensed with the attribution notes in PROFILE_LICENSE.md.
