# Public releases

The public source repository is [Nikon Recipes to LR Profiles](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles).

| Release | Profiles | Other assets |
|---|---|---|
| [v0.2.0](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/tag/v0.2.0) (current) | All 236 conversions use Y8; group **Nikon Recipes LR 0.2**, new names/UUIDs; tables byte-identical to the Y8 gallery downloads | Unchanged sample RAW ZIP re-attached |
| [v0.1.0](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/tag/v0.1.0) (historical) | 19 YC7 + 217 YC4; group **Nikon Recipes LR 0.1** | Sample RAWs, website assets 0.1.0 / 0.1.1 |

The rest of this page describes the first publication (0.1.0); its preparation rules still apply.

| Item | Prepared content |
|---|---|
| Identity | Nikon Recipes to LR Profiles / `Nikon-Recipes-to-LR-Profiles` |
| Scope | Nikon NP3 metadata, NX reference preparation, Z8 target/sample workflow, bounded tetrahedral fit, enhanced XMP codec, audit, optional Photoshop renderer |
| Profiles asset | 0.1.0: all 236 Nikon conversions, with 19 YC7 overrides and 217 YC4 conversions; new names/group/UUIDs. 0.2.0: all 236 Y8 |
| Sample asset | Four untouched original Z8 RAWs; original metadata publication authorized by the owner |
| Documentation | English primary; Chinese/Japanese installation, calibration, metrics and contribution guides; 236 recipe score pages, compact contact sheets and links to the hosted four-scene gallery |
| Licenses | MIT tool/original docs and project-created conversion resources; separate restricted sample/derived-photo permission |
| Community | Issues/PR templates, test workflow, CONTRIBUTING, `.github/FUNDING.yml` for b-z |
| Exclusions | Fuji conversion, original NP3 archive, SDK/vendor profiles, private research history, personal paths and large TIFF exports |

Neither profile pack claims that all 236 recipes have passed visual review. Banding remains a known issue and is prominently documented. The gallery includes all 944 owner-exported NX JPEG references (236 recipes on four scenes), alongside labeled numerical Lightroom previews checked against actual Camera Raw on three representative looks. It defaults to NX Studio versus our conversion; Adobe Standard is also selectable.

NX references were exported from untouched original copies with explicit ADL Off and color-only recipe settings. Earlier sanitized NEFs produced abnormal colors with NX sidecars while the untouched originals worked. The exact metadata mechanism remains unknown. The owner authorized publication of the original sample NEFs, so the sample asset and checksums now refer to those untouched files. Website derivatives contain no EXIF. Used batch RAW copies are deleted only after all JPEGs have been read and checked; original year-folder photos are preserved.

The static gallery is deployed separately through Cloudflare Direct Upload, without GitHub commits or pushes. See [Gallery workflow](GALLERY.md). It has the Landscape test 1 sidebar thumbnails, two landscapes before two banding scenes, and no detail thumbnails. The source-side compact NX/LR sheets contain eight recipes per JPEG, each with four NX/LR pairs (thirty sheets), ordered by ascending mean chart ΔE. The earlier full gallery ZIP is a preparation archive, not the current website or a final NX comparison asset.

Distribution: a profiles ZIP, a separate sample RAW ZIP and an independent website asset ZIP in the GitHub Release; contact sheets and scores stay with source documentation. Sponsor activation is completed by the owner.

Yunchuang remains the private research project. Emulsion is unrelated.

Website code is isolated in `website/`. The complete gallery image library and website asset ZIP are kept on external storage. `website/assets/` and `website/dist/` are ignored; documentation retains only a small example and 2024-pixel-wide contact sheets. Full gallery images are distributed separately in the website asset ZIP. The gallery offers slider comparison and synchronized A/B blinking at 1-second intervals.
