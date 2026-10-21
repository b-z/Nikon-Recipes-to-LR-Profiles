# Releasing

How a maintainer publishes a new profile release. Code-only changes do not need a release; they are listed under *Unreleased* in the [CHANGELOG](../CHANGELOG.md) until the next one.

## Conventions

- **Version**: `MAJOR.MINOR.PATCH` in `pyproject.toml` and `src/nikon_recipes_lr/__init__.py`; the Git tag is `v<version>`. A release that changes any profile table bumps at least the minor version.
- **Profile identity**: every release that changes profiles uses a new Profile Browser group (`Nikon Recipes LR <major>.<minor>/<creator group>`), a name suffix (`[NRLR <major>.<minor>]`) and new UUIDs (`uuid5(NAMESPACE_URL, "nikon-recipes-to-lr-profiles:<version>:<recipe>")`). Users can then install a new release next to the old one, and Lightroom never mixes two versions under one UUID.
- **Manifest**: `docs/release_manifest.json` lists every profile in the release: file name, UUID, SHA-256, RGBTable ID, attribution, chart scores (`fit`), banding audit (`banding`) and review notes. The catalog and the release ZIP are both checked against it.

## Steps

1. **Prepare the profiles.** Fit every recipe from its chart samples (`nikon-recipes-lr fit` or `nikon_recipes_lr.spline.SplineFitter`), apply the naming conventions above and write the manifest. The Z 8 calibration data and the batch script used for 0.2.0 are not public yet; publishing them is an open task.
2. **Check the profiles.** `nikon-recipes-lr audit` a sample, render a few through Camera Raw (`nikon-recipes-lr render`), and import the set into Lightroom to confirm the group, names and Amount slider.
3. **Update the repository.**
   - Bump the version in `pyproject.toml` and `src/nikon_recipes_lr/__init__.py`.
   - Replace `docs/release_manifest.json` and run `python scripts/write_catalog.py`.
   - Update the group name in `README.md`, `docs/*/README.md` and `docs/*/INSTALL.md` (the INSTALL files are copied into the ZIP).
   - Move the *Unreleased* CHANGELOG entries under the new version and describe the profile changes.
   - Open a pull request; CI checks that the catalog matches the manifest.
4. **Build the ZIP** from the merged commit:

   ```sh
   python scripts/package_release.py --profiles /path/to/profiles \
     --metrics docs/release_manifest.json --output /path/to/release-assets
   ```

   It refuses to build if a profile's checksum, UUID or table ID does not match the manifest, and writes `SHA256SUMS`. Add `--samples /path/to/raws` to rebuild the sample ZIP (only when the sample RAWs change).
5. **Publish** on GitHub with the tag `v<version>`, attaching the profiles ZIP, the sample RAW ZIP and `SHA256SUMS`. Summarize the CHANGELOG entry and the known limitations in the release notes.
6. **Update the website** if its profile downloads should follow the release ([website/README.md](../website/README.md)).

Earlier releases stay published so that users can return to them.
