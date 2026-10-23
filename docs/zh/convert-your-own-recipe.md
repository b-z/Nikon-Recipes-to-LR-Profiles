# 转换你自己的配方

[English](../en/convert-your-own-recipe.md) · [日本語](../ja/convert-your-own-recipe.md)

任何保存为 `.NP3` 文件的优化校准（Picture Control）或云创配方都可以转换成 Lightroom 配置文件，包括你自己创建的。工具会测量 NX Studio 套用你的配方后如何渲染一张色卡，再据此拟合配置文件，方法与 Release 中的配置文件相同。准备好环境之后，每款配方只需几分钟。

## 准备

- **`.NP3` 格式的配方。** 在相机上：「照片拍摄菜单 › 管理优化校准 › 载入/保存 › 复制到存储卡」，文件会写到存储卡的 `NIKON/CUSTOMPC` 文件夹。很多配方作者也会直接分享 NP3 文件。
- **[NX Studio](https://imaging.nikon.com/imaging/lineup/software/nx_studio/)**：尼康免费的 RAW 软件，支持 macOS 和 Windows。
- **Python 3.10 或更新版本。**
- **本仓库**：其中有工具本身和 [Z 8 校准包](../../calibration/z8/)，包括色卡 RAW、色块位置、NX Studio 设置以及对应的 Camera Raw 测量数据。不需要在 Lightroom 或 Photoshop 中渲染任何东西。

```sh
git clone https://github.com/b-z/Nikon-Recipes-to-LR-Profiles.git
cd Nikon-Recipes-to-LR-Profiles
python -m pip install -e .
unzip calibration/z8/chart.NEF.zip -d calibration/z8
```

下面的例子都在仓库文件夹中运行，并假设你的配方是 `MyRecipe.NP3`。

## 1. 为 NX Studio 准备色卡

```sh
nikon-recipes-lr prepare-nx --source calibration/z8/chart.NEF --template calibration/z8/nx-template.nksc \
  --recipes MyRecipe.NP3 --output nx-batch
```

这会生成 `nx-batch/MyRecipe.NEF`，并附带套用你配方的 NX Studio 设置。也可以一次列出多个 `.NP3` 文件。

## 2. 在 NX Studio 中导出色卡

1. 在 NX Studio 中打开 `nx-batch` 文件夹并选中色卡，调整面板中的优化校准应显示为你的配方。
2. 点击「导出」，格式选 **TIFF（16 位）**，保持原始尺寸，把 `MyRecipe.TIF` 保存在 NEF 旁边。校准包的设置已经使用 Adobe RGB 色彩空间。

色卡看起来是一行行彩色条纹；缩略图里可能仍显示制作色卡所用的原始照片，可以忽略。

## 3. 测量与拟合

```sh
nikon-recipes-lr sample nx-batch/MyRecipe.TIF --metadata calibration/z8/chart.json --output MyRecipe-nx.json
nikon-recipes-lr fit --adobe-samples calibration/z8/camera-flexible-color.npy --base "Camera Flexible Color" \
  --nx-samples MyRecipe-nx.json --name "MyRecipe" --author "你的名字" \
  --output MyRecipe.xmp --report MyRecipe-report.json
nikon-recipes-lr audit MyRecipe.xmp
```

- 如果 TIFF 不是与色卡同尺寸的 16 位 Adobe RGB，`sample` 会停止并给出提示。
- 输出中的 `mean_de` 是在色卡上与 NX Studio 的平均色差。低于 1 时肉眼很难分辨；Release 中的配置文件大约在 0.1 到 1.4 之间。
- `audit` 给出断层风险分（[分数说明](metrics.md)）。
- 如果想让 [`sidecars`](auto-apply.md) 自动套用，请把相机上显示的优化校准名称作为 `--name`。

这样得到的配置文件与 Release 中各机型的版本相同，以「相机 Flexible Color」为基础，限定 Z 8（其他机身请用对应的校准包，见[下文](#其他机身和自制色卡)）。如果想要像 Adobe 通用版那样以 Adobe Standard 为基础、适用于所有相机的配置文件，请改用 Adobe Standard 的测量数据，并去掉机型限制：

```sh
nikon-recipes-lr fit --adobe-samples calibration/z8/adobe-standard.npy --camera "" \
  --nx-samples MyRecipe-nx.json --name "MyRecipe" --author "你的名字" --output MyRecipe-any-camera.xmp
```

拟合只需几秒。用校准包按这种方法重新拟合 Release 中的配方，与已发布的配置文件平均相差约 0.1 ΔE。

## 4. 在 Lightroom 中使用

在配置文件浏览器中选择「导入配置文件」，导入 `MyRecipe.xmp`，它会出现在 **Nikon Recipes LR/Custom** 分组。正式使用之前，请在有平滑天空或焦外的照片上，用 100% 和更高的数量检查一下。与 Release 中的配置文件一样，它只复刻色彩和影调，配方中的锐化、中等锐化和清晰度不包含在内。

## 其他机身和自制色卡

仓库里为 Release 拟合过的每台机身都准备了校准包：[Z 8](../../calibration/z8/)、[Z 9](../../calibration/z9/)、[Z f](../../calibration/zf/)、[Z50II](../../calibration/z50ii/)、[Z6III](../../calibration/z6iii/) 和 [Z5II](../../calibration/z5ii/)。Camera Raw 和 NX Studio 对不同机身亮度的处理并不完全一致，所以其他机身请使用对应的校准包：`prepare-nx` 用它的 `chart.NEF`，`sample` 用它的 `chart.json`，`fit` 用它的 `camera-flexible-color.npy`，`--camera` 填它在 Camera Raw 中的型号名（例如 `"Nikon Z f"`，型号名列在 `src/nikon_recipes_lr/cameras.py` 中）。Z6III 和 Z5II 的校准包不含色卡 RAW，它们的 README 说明了如何用你自己的照片制作。

没有校准包的机身（例如 ZR），可以用 [`scripts/make_chart.py`](../../scripts/make_chart.py) 从这台相机的任意一张无损压缩或未压缩 NEF 制作色卡，用 NX Studio 和 Camera Raw 各渲染一次，再用 `sample` 测量 Camera Raw 的渲染结果。背景知识见[校准流程](calibration.md)（完整版为[英文](../en/calibration.md)）。非常欢迎贡献其他机身的校准包。
