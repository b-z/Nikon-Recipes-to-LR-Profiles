# Comparison gallery

[Live gallery](https://nikon-recipes-to-lr-profiles.pages.dev/) · [Website source and build](../website/README.md) · [NX / Lightroom contact sheets](comparisons/README.md)

The sidebar shows Landscape test 1 under every conversion. Sorting options are labeled Order by Name, Order by Chart ΔE and Order by Banding Risk. Wide screens show two scenes per row. The left and right image selectors independently choose Adobe Standard, NX Studio or Our LR conversion; a missing NX reference displays a placeholder, never another renderer under an NX label. Scene order is Landscape test 1, Landscape test 2, Banding test 1 (bokeh), Banding test 2 (sky). There are no separate detail thumbnails. All looks are shown at 100% Amount; the swipe slider changes only the comparison boundary.

The gallery includes all 944 maintainer-produced NX exports and defaults to NX Studio on the left and our conversion on the right. Adobe Standard remains available on either side. The right side is a numerical evaluation of the shipped tetrahedral Lightroom table, checked against Camera Raw exports for three representative looks. Small 8-bit display previews cannot establish the absence of subtle banding.

## Prepare NX references

Use independent copies of untouched original RAWs, one per recipe, with a saved NX sidecar containing the corresponding original recipe's color/tonal settings. Earlier metadata-sanitized samples were incompatible with this sidecar workflow even though their raw strips were unchanged. The maintainer has authorized original-file publication, so the current sample asset preserves complete original NEFs and their camera metadata. The precise cause of the earlier NX incompatibility is not established.

Leave as-shot white balance and zero exposure compensation. Disable sharpening/clarity and other detail processing, ADL, and optional optical corrections to match the color-only conversion scope. ADL must be explicitly Off rather than following the camera's setting. Verify the recipe name and settings in NX before starting a batch; sidecar parsing alone does not prove NX applied them. Record any lens correction NX forces on.

For gallery references, export JPEG at maximum quality, original dimensions, with sRGB conversion and an embedded ICC profile. Preserve filenames and export alongside the group's RAWs or into its `exports` folder; both locations are supported. Do not add output sharpening. [Official NX export instructions](https://nikonimglib.com/nxstdo/onlinehelp/en/saving_pictures_in_other_formats_64.html).

JPEG is sufficient for visual browsing; use 16-bit TIFF for fitting and precise banding checks. JPEG compression and 8-bit quantization can introduce or mask weak bands.

## Ingest and stage

Install the package's dependencies first. The private batch manifest maps each filename to a scene and recipe; original NP3 files and NX sidecars are not included in the public source.

```sh
PYTHONPATH=src python3 website/scripts/ingest_nx_gallery.py --batch /path/to/nx-batch --assets /path/to/website-assets
PYTHONPATH=src python3 website/scripts/build_site.py --assets /path/to/website-assets --output website/dist
```

The ingest step reads only named JPEG exports, requires ICC profiles, creates sanitized sRGB derivatives, updates the gallery reference data, and generates contact sheets (eight recipes per JPEG, with all four NX/LR scene pairs per row, sorted by ascending mean chart ΔE). Missing exports remain explicitly pending. Partial batches are supported. Keep all full-size exports and the complete gallery image library on external storage. `website/` holds the template, scripts and asset inventory; Git documentation contains only compact sheets and a small example. See the [website build guide](../website/README.md).

The static staging step copies only public gallery/documentation assets and photo permission notices. It excludes RAWs, TIFFs, NP3s, NX sidecars, credentials, source code and private research files. It adds the root gallery redirect. Deployment is independent of Git commits and pushes:

```sh
npx wrangler pages deploy website/dist --project-name nikon-recipes-to-lr-profiles --branch main --commit-dirty=true
```

This command uploads files; it does not commit or push the repository. Photos and derivatives use the [restricted project comparison permission](../samples/LICENSE.md), not MIT.
