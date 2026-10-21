# Nikon Recipes to LR Profiles

[English](../../README.md) · [日本語](../ja/README.md)

在 Lightroom / Camera Raw 中使用尼康云创（Nikon Imaging Cloud）**配方（Imaging Recipe）** 的风格，并用 **0–200% 的数量滑块**调节强度。曝光、白平衡等 RAW 调整照常可用。

当前版本包含 **236 款配方转换**，格式为基于 Adobe Standard 的增强配置文件 `.xmp`，不需要 DCP 或安装程序。每款都按 NX Studio 的渲染结果拟合，是对配方的近似，不是尼康的渲染引擎，也不是把 NP3 滑块逐项翻译成 LR 参数。

## 使用配置文件

1. 从[最新 Release](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest) 下载 `nikon-recipes-lr-profiles-<版本>.zip` 并解压。
2. 在 Lightroom 或 Camera Raw 的配置文件浏览器中选择「导入配置文件」，选中 `profiles/` 里的 `.xmp`。如果没有出现，重启 Lightroom。
3. 打开 **Nikon Recipes LR 0.2** 分组，选择风格并调整数量。想要温和效果可以先试 30–50%。

新版本的配置文件使用新的分组和 ID，可以与旧版本并存；不再需要时删除旧分组即可。详见[安装说明](INSTALL.md)。

## 对比各个配方

- **[在线对比图库](https://nikon-recipes-to-lr-profiles.pages.dev/)**：每款配方在四张照片上的效果，NX Studio 与 LR 转换并排对比，支持 A/B 闪烁切换和单独下载。
- **[配方目录](../RECIPES.md)**：作者署名、拟合误差和断层风险分（[分数说明](metrics.md)）。

## 原理

1. 一张包含约 24,000 个色块的合成标靶 RAW 分别渲染两次：NX Studio 套用配方，Camera Raw 使用 Adobe Standard。
2. 拟合一个从 Adobe 颜色到 NX 颜色的平滑、有界的三维映射。0.2.0 起使用每轴 16 个控制点的三次样条（[方法说明](../Y8_REBUILD.md)），比直接拟合颜色表的渐变更平滑。
3. 映射以 32³ RGB 表的形式存进叠加在 Adobe Standard 上的 Lightroom「外观」配置文件，数量滑块控制与原图的混合比例。

NP3 文件只提供配方名称等元数据，颜色来自 NX Studio 的实际渲染。

## 已知限制

- **色彩断层。** 平滑的天空和焦外仍可能出现台阶，强度越高越明显。上一版有断层的 58 款已在多张照片上复查，未见断层；其余 178 款没有逐一复查。发现问题欢迎[反馈](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose)。
- **机身。** 目前只在 Nikon Z 8 上校准和测试，其他机身可能有差异。
- **范围。** 只还原色彩和整体影调；锐化、清晰度、颗粒、暗角和镜头校正请在 Lightroom 中自行设置。
- **近似。** 236 款中有 197 款与 NX Studio 的平均标靶色差低于 1 ΔE（CIEDE2000），最大 1.85 ΔE；个别颜色和照片的差异可能更大。

## 自己校准配方

需要同一张标靶在 NX Studio 和 Camera Raw 中的渲染结果。流程见[校准说明](calibration.md)（完整版为[英文](../en/calibration.md)），命令示例见[英文 README](../../README.md#calibrate-a-recipe-yourself)。

## 参与贡献

欢迎贡献其他尼康机身的校准、可复现的断层反馈、更平滑的拟合方法、测试和翻译。请先阅读[贡献指南](CONTRIBUTING.md)，并遵守[行为准则](../../CODE_OF_CONDUCT.md)。版本变化见 [CHANGELOG](../../CHANGELOG.md)。

## 支持项目

如果这些配置文件对你有帮助，可以通过 [GitHub Sponsors](https://github.com/sponsors/b-z) 支持项目。赞助完全自愿，不影响 Issue 和 PR 的处理。

## 署名与许可

- 配方归各自作者所有，每个配置文件和目录中都有署名。本项目不分发原始 NP3 文件，请从作者、Nikon Imaging Cloud 或 [Nikon-Recipes 合集](https://github.com/shouryan01/Nikon-Recipes)获取。
- 代码与文档采用 [MIT](../../LICENSE)；生成的配置文件采用 MIT 并附[署名说明](../../PROFILE_LICENSE.md)。第三方说明见 [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md)。
- 四张样本照片及其衍生图像**不适用** MIT，仅可用于本项目的测试和对比，见[照片条款](../../samples/LICENSE.md)。

本项目为独立的社区项目，与 Nikon、Adobe 无关联，也未获其认可。
