# Website source and external assets

The [live comparison gallery](https://nikon-recipes-to-lr-profiles.pages.dev/) is a separate static build. The repository contains its template, scripts and metadata, **not the complete image library**. Normal profile use does not require building the website.

| Location | Contents | Stored in Git |
|---|---|---|
| `website/gallery.template.html` | Gallery UI | Yes |
| `website/scripts/` | Preview generation, NX import and site builder | Yes |
| `website/data/` | Reference metadata, provenance and SHA-256 asset inventory | Yes |
| `docs/images/`, `docs/comparisons/` | Small example and compact contact sheets | Yes |
| External asset directory | Complete `images/`, `comparisons/` and downloadable `profiles/` folders | No |
| `website/assets/` | Optional local extraction location for the asset pack | No |
| `website/dist/` | Generated deployable site | No |

## Build

Install the project's dependencies (`python -m pip install -e .`). Obtain the separate `nikon-recipes-lr-website-assets-0.1.1.zip` asset pack and extract it outside the checkout or into the ignored `website/assets/` directory. Download it from the [v0.1.0 Release](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/tag/v0.1.0). Maintainers can instead use the external asset directory directly.

```sh
PYTHONPATH=src python3 website/scripts/build_site.py --assets /path/to/website-assets
```

Alternatively set `NIKON_LR_WEBSITE_ASSETS` and omit `--assets`. The default output is `website/dist/`; `--output /path/to/empty-directory` overrides it. Output must be empty to avoid stale assets. The builder verifies every listed asset's SHA-256 while copying it, restores full website-only recipe previews, and checks that all NX references and conversions exist. It never writes full-size images or generated HTML into repository documentation.

Open `website/dist/docs/gallery.html`, or serve `website/dist/` with any static server. Existing public URLs under `/docs/` are preserved. RAW files, source recipes, NX sidecars, credentials and developer caches are excluded.

## Update references

NX JPEGs may sit alongside the batch RAW names or under `exports/`. Keep originals on external storage.

```sh
PYTHONPATH=src python3 website/scripts/ingest_nx_gallery.py --batch /path/to/nx-batch --assets /path/to/website-assets
```

This updates website reference metadata and the asset inventory, writes full-size gallery previews and sheets only into the external assets, and refreshes compact documentation sheets and score pages. Rebuild the asset pack after changing assets; old packs intentionally fail the new inventory check. Numerical conversion previews can be regenerated with `website/scripts/build_gallery.py --profiles ... --baselines ... --metrics docs/recipe_metrics.json --assets ...`.

Deploy `website/dist/` with Cloudflare Pages Direct Upload. Deployment does not require a Git commit or push. All photographs and derivatives follow [sample photo terms](../samples/LICENSE.md); they are not MIT-licensed.

中文：完整图库素材保存在仓库之外；仓库只保留网站代码、素材清单和小尺寸文档图。构建产物 `website/dist/` 不进入 Git。

日本語：完全な画像素材はリポジトリ外に保存し、ソースにはサイトコード、素材一覧と小さな文書用画像のみを含めます。`website/dist/` は Git に追加しません。

The gallery defaults to synchronized A/B blinking every second. Arrow Up / Arrow Down selects the previous / next recipe in the visible filtered/sorted list. The NP3 button links to the credited upstream archive; the XMP button downloads the exact converted profile. Original NP3s are not hosted here.

Use the heart beside each recipe to save favorites in this browser’s local storage. Favorites persist across reloads and are not uploaded or shared between devices. Clearing site data removes them.

Neutral warning triangles mark the 58 recipes with residual banding in the owner’s Y7 review on 2026-10-10. They replace the previous yellow/gray classification. The fixed list is in `data/banding_warnings.json`; favorites remain browser-local and independent of it. [Review](../docs/BANDING_REVIEW.md). `Order by Favorites` is unchanged.

The gallery defaults to Y8 smooth-function conversions. Select Y7 or `Previous LR conversion` to compare older versions. The XMP button explicitly labels and downloads the displayed conversion version (right-hand LR source takes priority). All236 Y8 profiles and four-scene previews are stored as separate external assets; Y7 and NX are preserved. The 58 historical Y7 warning recipes passed the owner's latest Y8 real-photo review, with no banding observed. This is not a universal guarantee. GitHub release assets remain a separate historical snapshot until explicitly updated.
