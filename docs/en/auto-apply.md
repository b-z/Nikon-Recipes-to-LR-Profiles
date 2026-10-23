# Apply profiles automatically

[中文](../zh/auto-apply.md) · [日本語](../ja/auto-apply.md)

When a Nikon camera takes a photo, it stores the name of the active Picture Control in the NEF. For an Imaging Recipe this is the recipe's own name, for example `KP160`. The `nikon-recipes-lr sidecars` command reads that name and writes an XMP sidecar (`_DSC1234.xmp`) next to each NEF that selects the matching profile. Lightroom Classic and Camera Raw read the sidecar, so the photo opens with the recipe already applied. You can change or remove the profile like any other edit.

## What you need

- The unzipped profiles of a release, the same files you imported into Lightroom.
- Python 3.10 or newer, and this project's tool:

  ```sh
  python -m pip install "git+https://github.com/b-z/Nikon-Recipes-to-LR-Profiles.git"
  ```

- [ExifTool](https://exiftool.org/), which reads the camera data (macOS with Homebrew: `brew install exiftool`).

## Steps

1. Copy the photos from the card to a folder, as you would before importing.
2. See what would happen, without writing anything:

   ```sh
   nikon-recipes-lr sidecars --dry-run --profiles ~/Downloads/nikon-recipes-lr-profiles-1.0.1-z8/profiles ~/Pictures/2026-10-18
   ```

   `written` lists the photos that would get a sidecar and the profile for each; `no_profile` counts photos taken with a Picture Control that has no profile, such as Standard.
3. Run the same command without `--dry-run`.
4. Import the folder into Lightroom Classic. Camera Raw (Photoshop or Bridge) picks up the sidecars when you open the files.

Add `--recursive` to include subfolders and `--amount 0.5` to start at 50% instead of 100%.

**Already imported?** Run the command on the folder, then select the photos in Lightroom Classic and choose **Metadata › Read Metadata from Files**. This replaces the develop settings of those photos with the sidecar, so do it before you start editing them.

## What the sidecar contains

- The recipe's profile at the chosen Amount, on its base profile (Camera Flexible Color in the camera packs, Adobe Standard in the Adobe pack).
- Lens profile corrections switched on, as Camera Raw does for new photos.

Everything else is left out, so Camera Raw uses its built-in defaults for it. A custom Raw Defaults preset is not applied to photos that have a sidecar; apply your preset after import if you use one. A preset that includes a profile replaces the recipe's profile.

## Matching rules

- **Release profiles** are found by file name, and each recipe's Picture Control name comes from its NP3 file. All 236 names are different, so a photo never matches two recipes.
- **Your own profiles** ([Convert your own recipe](convert-your-own-recipe.md)) are matched by profile name. Use the Picture Control name shown on the camera as `--name` when you fit the profile.
- Photos with an existing sidecar are skipped. `--overwrite` replaces the sidecar, and any edits stored in it are lost.
- Only `.NEF` and `.NRW` files are read; the original files are never changed.

The command has been checked with Lightroom Classic and Camera Raw. Reports from the cloud-based Lightroom app are welcome in the [issues](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues).
