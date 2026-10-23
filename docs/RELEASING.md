# Releasing

How a maintainer publishes a new profile release. Code-only changes do not need a release; they are listed under *Unreleased* in the [CHANGELOG](../CHANGELOG.md) until the next one.

## Conventions

- **Version**: `MAJOR.MINOR.PATCH` in `pyproject.toml` and `src/nikon_recipes_lr/__init__.py`; the Git tag is `v<version>`. A release that changes any profile table bumps at least the minor version.
- **Profile identity**: every release that changes profiles uses a new Profile Browser group (`Nikon Recipes LR <major>.<minor>/<creator group>`), a name suffix (`[NRLR <major>.<minor>]`) and new UUIDs (`uuid5(NAMESPACE_URL, "nikon-recipes-to-lr-profiles:<version>:<recipe>")`). Users can then install a new release next to the old one, and Lightroom never mixes two versions under one UUID.
- **Manifest**: `docs/release_manifest.json` lists every profile in the release: file name, UUID, SHA-256, RGBTable ID, base profile, camera restriction, Picture Control name, attribution, chart scores (`fit`), banding audit (`banding`) and the scores of the previous release. The catalog, the release ZIP and the website are all checked against it. The manifest of 0.2.0 is kept in `website/data/release_0.2.0_manifest.json` because the website still offers those profiles for cameras other than the Z 8.

## Steps

1. **Prepare the profiles.** Make one NX Studio export of the [Z 8 calibration kit](../calibration/z8/) chart per recipe (`prepare-nx` for all NP3 files at once), then run

   ```sh
   python scripts/build_release_profiles.py --nx /path/to/nx-batch --version <version> --np3 /path/to/Nikon-Recipes --output /path/to/new-release
   ```

   It samples every TIFF, fits on the kit's fixed training patches, scores the held-out patches, audits banding risk, and writes the reference (Nikon Z 8) profiles with the naming conventions above plus a manifest; copy that manifest to `docs/release_manifest.json` after adding each row's `previous` scores. Refitting a released recipe this way reproduces its table within about 0.06 ΔE.

   Repeat this for every other body with a kit (`calibration/<camera>/`): `prepare-nx` with that kit's `chart.NEF` (or the chart made with `scripts/make_chart.py` for kits without one), one NX Studio export, then `build_release_profiles.py --camera <camera>`. Copy each manifest to `docs/camera_manifests/<camera>.json` and keep the profiles in one folder per camera (`<camera-profiles>/<camera>/`); only their color tables are used.
2. **Check the profiles.** `nikon-recipes-lr audit` a sample, render a few through Camera Raw (`nikon-recipes-lr render`), and import the set into Lightroom to confirm the group, names and Amount slider.
3. **Update the repository.**
   - Bump the version in `pyproject.toml` and `src/nikon_recipes_lr/__init__.py`.
   - Replace `docs/release_manifest.json` and run `python scripts/write_catalog.py`.
   - If recipes were added or renamed, run `python scripts/write_picture_controls.py /path/to/Nikon-Recipes` so that `nikon-recipes-lr sidecars` recognises them.
   - Update the version and group name in `README.md`, `docs/*/README.md` and `docs/*/INSTALL.md`. The three INSTALL files become the `README.md` inside the ZIP, so they must explain installing and using the profiles on their own.
   - Move the *Unreleased* CHANGELOG entries under the new version and describe the profile changes.
   - Open a pull request; CI checks that the catalog matches the manifest.
4. **Build the ZIPs** from the merged commit: one per Camera Flexible Color body (listed in `src/nikon_recipes_lr/cameras.py`) and one Adobe pack, all with the same version:

   ```sh
   python scripts/package_release.py --profiles /path/to/reference-z8-profiles \
     --camera-profiles /path/to/camera-profiles --previous-profiles /path/to/0.2.0/profiles \
     --output /path/to/release-assets
   ```

   It refuses to build if a reference profile's checksum or a camera table does not match its manifest. Each camera pack is the reference profile with that camera's restriction, UUID and color table; the website makes its per-recipe downloads with the same functions.
5. **Publish** on GitHub with the tag `v<version>`, attaching only the profile ZIPs, so that the release page stays simple for people who only want the profiles. GitHub adds *Source code* archives to every release automatically; they cannot be removed. In the release notes, summarize the CHANGELOG entry and the known limitations, explain which pack is for which camera and how the packs differ, and point to the [gallery](https://nikon-recipes-to-lr-profiles.pages.dev/) for downloading single recipes.
6. **Update the website** so that its previews and per-recipe downloads match the release: `website/scripts/make_previews.py` for new tables, then `build_site.py` and deploy ([website/README.md](../website/README.md)).

Earlier releases stay published so that users can return to them.

## Files that are not profile releases

- **Sample RAWs** (`nikon-recipes-lr-samples-0.1.0.zip`) stay on the [v0.1.0 release](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/tag/v0.1.0) together with the website asset pack. Only if the photographs change, build a new sample ZIP with `package_release.py --samples /path/to/raws` and publish it the same way.
- **Calibration kits** live in the repository under `calibration/<camera>/`: the chart RAW (zipped), `chart.json` (patch positions in the format of `nikon-recipes-lr sample`), the NX Studio template and one Camera Raw baseline per base profile, sampled with `nikon-recipes-lr sample`. If any of these change, profiles fitted before and after are no longer comparable, so note the change in the CHANGELOG and in the kit's README.

## Adding new recipes

Recipe IDs are the NP3 file names of the [Nikon-Recipes archive](https://github.com/shouryan01/Nikon-Recipes) with spaces replaced by underscores; the archive commit is recorded in `website/data/downloads.json`.

1. **Find new recipes.** Update a local clone of the archive and list NP3 files whose ID is not in `docs/release_manifest.json`. Recipes from Nikon Imaging Cloud that are not in the archive can be copied from a camera to a memory card (*Manage Picture Control › Load/save › Copy to memory card*); credit the recipe's creator, not the person who copied it, and add the file to the archive by pull request if its license allows.
2. **Calibrate** each new NP3 with the current calibration kit exactly as in [Convert your own recipe](en/convert-your-own-recipe.md): `prepare-nx` for all new files at once, one NX Studio export, then `sample` and `fit`. Keep the NX TIFFs on external storage; they are the expensive part to redo.
3. **Review** the new profiles with `audit`, a few Camera Raw renders and the gallery previews, as for any release.
4. **Release** them following the steps above. Adding recipes changes the profile set, so it is at least a minor version with a new group and new UUIDs for every profile.
