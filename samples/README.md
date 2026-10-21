# Z8 comparison samples

Download the separate `nikon-recipes-lr-samples-0.1.0.zip` sample asset from [Releases](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases) (attached to both 0.1.0 and 0.2.0; the RAWs are unchanged). This keeps roughly 200 MB of RAW files out of normal source clones. The four RAWs are still part of the project's published benchmark inputs.

| File | Purpose |
|---|---|
| `_DSC2694.NEF` | Bokeh gradients / banding |
| `_DSC5054.NEF` | Sky gradients / banding |
| `_DSC9046.NEF` | Landscape color style |
| `_DSC2849.NEF` | Landscape color style |

Read [photo permission](LICENSE.md) before reuse. `manifest.json` records original-file and raw-strip SHA-256 hashes. These photos are benchmark inputs, not universal chart donors. Published previews are also governed by the photo terms.

## Original NEFs and NX compatibility

The photographer (the project maintainer) authorized publication of these four untouched original NEFs, including their camera metadata. They replace the earlier metadata-sanitized copies: in the six-case test, sanitized NEFs rendered normally alone but produced abnormal colors with NX recipe sidecars; untouched originals worked with both tested sidecars. The precise metadata mechanism is unknown. Keeping original files preserves compatibility with this NX workflow. The web gallery contains only rendered JPEG derivatives without EXIF, not RAW files.

经照片作者授权，样本改为未脱敏、未修改的原始 NEF，保留相机元数据，供 Adobe/Lightroom 和 NX 测试。此前脱敏片搭配 NX 侧车颜色异常。网页只使用无 EXIF 的 JPEG 衍生图。

撮影者の許可により、サンプルはカメラ情報を保持した未変更のオリジナル NEF に置き換えました。Adobe/Lightroom と NX のテストに使用できます。以前の匿名化済みファイルは NX サイドカーと組み合わせると異常な色が出ました。Web ギャラリーには EXIF を含まない JPEG 派生画像のみを掲載します。
