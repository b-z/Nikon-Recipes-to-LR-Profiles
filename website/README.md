# Website

The [online gallery](https://nikon-recipes-to-lr-profiles.pages.dev/) is a single static page built from `gallery.template.html`, the release manifests and an image library that is kept outside Git. Using the profiles does not require building the website.

| Location | Contents | In Git |
|---|---|---|
| `website/gallery.template.html` | The page: layout, texts in English, Chinese and Japanese, and all scripts | Yes |
| `website/payment.js` | WeChat reward QR code, shown only if its SHA-256 matches the value in the same file | Yes |
| `website/data/` | NX Studio reference list, per-recipe download paths, the 0.2.0 manifest and the historical Y7 banding list | Yes |
| `website/scripts/make_previews.py` | Makes the image library | Yes |
| `website/scripts/build_site.py` | Assembles the deployable site | Yes |
| Image library | About 4,000 JPEG previews (1280 px) | No |
| `website/dist/` | Generated site | No (ignored) |

## Make the image library

`make_previews.py` needs Camera Raw renders of the four sample RAWs (on the v0.1.0 release) with both base profiles, NX Studio JPEG exports of every recipe on every scene ([how to prepare them](../docs/GALLERY.md)), and the profiles of the current release and of 0.2.0. Its docstring lists the exact file names. All previews come out at 1280 px through the same steps, so blinking between sources never changes sharpness.

```sh
python website/scripts/make_previews.py --renders /path/to/renders --nx /path/to/nx-exports \
  --profiles /path/to/nikon-recipes-lr-profiles-1.0.0/profiles \
  --previous-profiles /path/to/nikon-recipes-lr-profiles-0.2.0/profiles --output /path/to/library
```

Existing images are kept, so the command can be rerun after adding recipes.

## Build and deploy

```sh
python website/scripts/build_site.py --images /path/to/library/images \
  --profiles /path/to/nikon-recipes-lr-profiles-1.0.0/profiles \
  --previous-profiles /path/to/nikon-recipes-lr-profiles-0.2.0/profiles
npx wrangler pages deploy website/dist --project-name nikon-recipes-to-lr-profiles --branch main --commit-dirty=true
```

`build_site.py` writes `website/dist/` (use `--output` for another empty folder). It checks every profile against `docs/release_manifest.json` or the 0.2.0 manifest, fails if any preview the page links to is missing, and adds redirects for the addresses of the earlier gallery (`/docs/gallery.html` and `/docs/*`). Deploying uploads files with Cloudflare Pages Direct Upload; it does not need a commit. All photographs and previews follow the [sample photo terms](../samples/LICENSE.md), not MIT.

## How the page behaves

- English, Chinese and Japanese (`?lang=en|zh|ja`, otherwise the browser language). A help dialog explains the project on the first visit and can be reopened from **Help**; it has its own language menu.
- The download buttons open a short explanation first (which release is for which camera, and that single recipes can be downloaded) before linking to the release on GitHub.
- The recipe list can be shown by folder (the folder structure of the NP3 archive, the default), by name, by difference from NX Studio, by banding risk or with favorites first. Search also matches creators and folders. The default recipe is KG200P1.
- Image A and image B can each show NX Studio, the 1.0 or 0.2 profile, or Adobe Standard / Camera Flexible Color without a recipe. Blink mode switches every second and pauses when an image is clicked; the slider shows A on the left and B on the right. Arrow keys select the previous or next recipe in the visible list.
- **Download this recipe** downloads the release profile of the version shown as image B (1.0 unless 0.2 is selected). The NP3 button links to the credited upstream archive; original NP3 files are not hosted here.
- Favorites, language, list order and comparison settings are stored only in the browser's local storage.
- The Sponsor dialog shows GitHub Sponsors and the WeChat QR code from `payment.js`.

Image folders keep the internal method names: `images/y9` holds the 1.0 previews and `images/y8` the 0.2 previews.
