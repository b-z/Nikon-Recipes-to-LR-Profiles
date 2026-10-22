# 自动套用配置文件

[English](../en/auto-apply.md) · [日本語](../ja/auto-apply.md)

尼康相机拍照时，会把当前使用的优化校准（Picture Control）名称记录在 NEF 里；如果用的是云创配方，记录的就是配方自己的名称，例如 `KP160`。`nikon-recipes-lr sidecars` 命令读出这个名称，在每个 NEF 旁边写一个选中对应配置文件的 XMP 附属文件（如 `_DSC1234.xmp`）。Lightroom Classic 和 Camera Raw 会读取这个文件，所以照片打开时就已经套用了配方。之后可以像其他调整一样更换或去掉配置文件。

## 准备

- 解压后的 Release 配置文件，也就是你导入 Lightroom 的那些文件。
- Python 3.10 或更新版本，以及本项目的工具：

  ```sh
  python -m pip install "git+https://github.com/b-z/Nikon-Recipes-to-LR-Profiles.git"
  ```

- 用于读取相机数据的 [ExifTool](https://exiftool.org/)（macOS 上可用 Homebrew：`brew install exiftool`）。

## 步骤

1. 和平时导入前一样，把照片从存储卡复制到一个文件夹。
2. 先预览结果，不写入任何文件：

   ```sh
   nikon-recipes-lr sidecars --dry-run --profiles ~/Downloads/nikon-recipes-lr-profiles-1.0.0/profiles ~/Pictures/2026-10-18
   ```

   `written` 列出将要写入附属文件的照片及各自的配置文件；`no_profile` 统计用没有对应配置文件的优化校准（例如「标准」）拍摄的照片。
3. 去掉 `--dry-run` 再运行一次。
4. 在 Lightroom Classic 中导入这个文件夹。Camera Raw（Photoshop 或 Bridge）打开文件时会自动读取附属文件。

加 `--recursive` 可以包含子文件夹；加 `--amount 0.5` 可以让数量从 50% 而不是 100% 开始。

**已经导入了？** 对该文件夹运行命令后，在 Lightroom Classic 中选中这些照片，选择「元数据 › 从文件读取元数据」。这会用附属文件替换这些照片的修改设置，所以请在开始修图之前进行。

## 附属文件里有什么

- 配方的配置文件和所选的数量，以及它的基础配置文件（1.0 为「相机 Flexible Color」，0.2 为 Adobe Standard）。
- 开启镜头配置文件校正，与 Camera Raw 对新照片的默认做法一致。

其他设置都不写入，由 Camera Raw 使用内置默认值。带有附属文件的照片不会应用你自定义的 Raw 默认设置；如果你平时使用预设，请在导入后再应用。包含配置文件的预设会替换掉配方的配置文件。

## 匹配规则

- **Release 中的配置文件**按文件名识别，每款配方的优化校准名称取自它的 NP3 文件。236 个名称互不相同，一张照片不会同时匹配两款配方。
- **你自己转换的配置文件**（[转换你自己的配方](convert-your-own-recipe.md)）按配置文件名称匹配。拟合时请把相机上显示的优化校准名称作为 `--name`。
- 已有附属文件的照片会被跳过。`--overwrite` 会替换附属文件，其中保存的修改将会丢失。
- 只读取 `.NEF` 和 `.NRW` 文件，原始文件不会被修改。

这个命令已经在 Lightroom Classic 和 Camera Raw 中验证；欢迎在 [Issues](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues) 中反馈 Lightroom（云端版）中的使用结果。
