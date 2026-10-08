# Calibration workflow

## Inputs and export settings

Use the same synthetic RAW and patch-center metadata for both renderers. Export **16-bit RGB TIFF in Adobe RGB (1998)**, at original dimensions. Disable Nikon ADL, noise reduction, sharpening, clarity and optical corrections where the body/lens permits; record any control that cannot be disabled. Use an Adobe Standard baseline with As Shot white balance, a linear user curve and zero Basic/detail adjustments. Do not compare differently cropped or resized targets.

Our NP3 reader exposes Nikon's TLV metadata. Curves, Color Blender and Color Grading have mathematical parameters, but their processing space/order and interactions differ from Adobe's controls. The released workflow therefore fits measured NX output. It is not a claim that white-box decomposition is impossible; exact component mapping remains future research.

## 1. Make a chart (experimental)

```sh
nikon-recipes-lr make-target --donor donor.NEF --output chart.NEF   --confirm-donor-calibration
```

The donor must be little-endian Nikon Z 8 RAW with a unique 8280×5520 raw IFD and a single raw strip at the end of the file. This experimental generator uses calibration constants from the development donor: RGGB layout, 12/8 inset, black level 1008, highlight limit 15311 and WB multipliers 1.85156/1/1.42578. **A Z8 model name alone does not establish compatible metadata.** Confirm donor black level, CFA, white balance and dimensions before using the flag; otherwise provide your own synthetic target and metadata. Donor JPEG previews are retained and can show the original photo; evaluate the RAW render. No donor file is bundled as a universal calibration donor.

The chart samples 48 hue angles × 21 nonuniform saturation levels × 24 brightness levels, with 240 extra neutral patches, at 40-pixel pitch. This is not a claim that the chart reaches every possible sensor color or guarantees camera-independent calibration. Output is about 92 MB; use your own large-data directory. The observed Nikon uncompressed layout stores 14-bit codes in unpacked 16-bit containers; ExifTool may issue a minor StripByteCounts warning because the nominal bit-depth tag remains 14. The development donor output was verified in Camera Raw. Modified donors whose metadata editing appended data after the raw strip are intentionally rejected; use an untouched compatible donor.

## 2. Export NX references

Save one properly configured NX Studio chart adjustment to an `.nksc` sidecar. Supply that template and your own NP3 files:

```sh
nikon-recipes-lr prepare-nx --source chart.NEF --template chart.NEF.nksc   --recipes recipe-a.NP3 recipe-b.NP3 --output nx-batch
```

Open the new batch directory in NX Studio. Verify the named Picture Control and detail/lens settings on a sample, then export all references. Sidecar injection preserves the template's other settings; it does not validate or disable them for you. It requires the observed escaped ExportData/CustomData layout and fails on unsupported templates. No supported public NX command-line renderer is used here.

## 3. Sample TIFFs

```sh
nikon-recipes-lr sample adobe.TIF --metadata chart.json --output adobe.json
nikon-recipes-lr sample recipe-a.TIF --metadata chart.json --output nx.json
```

The sampler handles sensor dimensions or the 8256×5504 active crop by explicit metadata offsets. It requires 16-bit RGB and an embedded Adobe RGB ICC profile; it samples patch interiors without converting to 8-bit.

Optional macOS + Photoshop + ExifTool baseline export:

```sh
nikon-recipes-lr render chart.NEF --output adobe.TIF
```

This uses a disposable local RAW copy and embedded sidecar, leaves the original file and Photoshop documents alone, and does not install a profile or restart Photoshop. Only the document opened by the command is closed. TIFF output can be written to a large external volume; local scratch files are removed after the command. Other platforms can export manually in Camera Raw/Lightroom.

## 4. Fit, audit and review

```sh
nikon-recipes-lr fit --adobe-samples adobe.json --nx-samples nx.json   --name "Recipe A" --author "Original author" --output recipe-a.xmp   --grid 32 --lambda 0.5 --report recipe-a-report.json
nikon-recipes-lr audit recipe-a.xmp
```

The bounded solver fits encoded RGB with a penalty on every tetrahedral face and a small identity ridge. It quantizes to 16-bit table nodes. `--lambda` controls the fidelity/smoothness tradeoff; 0.5 is the YC7 development setting, not a proven optimum for every recipe. The CLI fit report is a training-set score. For development, use separate calibration/validation pairs and actual RAW scenes; do not tune on a test split and still call it unseen validation.

Import the enhanced `.xmp` manually, restart Lightroom if needed, and inspect smooth gradients, skies and bokeh at both normal strength and 200%. Changing the profile can change exposure/WB slider feel. Do not overwrite existing edits when preparing benchmarks.

Amount blends the table with identity in its encoded RGB working space; it is not byte-for-byte blending of two finished JPEGs, and Amount does not mean every Nikon slider was reduced by that percentage. Profile-induced display clipping can change when exposure is lowered; sensor clipping cannot be restored. The earlier exposure-recovery experiment does not certify every recipe at every setting.
