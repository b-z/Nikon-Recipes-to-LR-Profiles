# Nikon Recipes to LR Profiles

[English](../../README.md) · [日本語](../ja/README.md)

把尼康云创配方的色彩风格带进 Lightroom / Camera Raw，并使用 **0–200% 的数量滑块**调节强度。曝光、白平衡等后期操作仍可照常使用。

Release 0.2.0 包含 **236 款尼康配方转换**，全部使用更平滑的 **Y8** 方法拟合，格式为基于 Adobe Standard 的增强配置文件 `.xmp`，无需额外 DCP 或安装包。目前实测机身是 **Nikon Z8**。这是通过 NX 真值标靶拟合的近似转换，不是把 NP3 滑块直接翻译成 LR，也不保证与尼康渲染完全一致。

1. 从 [Releases](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases) 下载并解压配置文件 ZIP。
2. 在 LR / Camera Raw 的配置文件浏览器中手动导入 `.xmp`；若未显示，重启 LR。
3. 打开 **Nikon Recipes LR 0.2** 分组，选择风格并调整数量。温和使用可以先试 30–50%，再调整曝光和白平衡。0.2.0 使用新的名称、分组和 UUID，可与 0.1 并存；不需要时可删除 **Nikon Recipes LR 0.1** 分组。

[逐款评分与目录](../RECIPES.md) · [在线对比图库](https://nikon-recipes-to-lr-profiles.pages.dev/) · [网站构建](../../website/README.md) · [拟合流程](calibration.md) · [分数定义](metrics.md)

图库默认对比 NX 原版与 Y8 转换，也可切换 Adobe Standard、Y7 和更早版本；左侧是所有配方的风景缩略图，两张风景图排在两张断层测试图前。仓库内的 [NX/LR 对比拼图](../comparisons/README.md)仍是 Y7 版本。

**色彩断层是已知问题。** Y8 牺牲少量格靶精度换取更平滑的渐变，236 款中 214 款格靶 ΔE 比 Y7 高（中位数 0.47 → 0.70，见[目录](../RECIPES.md)），断层风险分中位数 0.51 → 0.46。Y7 中仍有断层的 58 款，作者已用 Y8 在多张实拍上复查，未见断层；其余 178 款未逐一复查。[Y8 方法与复查](../Y8_REBUILD.md)。0.1.0 Release（19 款 YC7 + 217 款 YC4）保留为历史下载。低 ΔE 或低风险分不代表所有照片没有断层。对比图默认是 Adobe Standard 导出上的数学预览，不是 NX 真值；实际 Camera Raw 验证另行标记。

原始 NP3 请从作者或 [Nikon-Recipes](https://github.com/shouryan01/Nikon-Recipes) 获取，本仓库不打包原件。富士胶片模拟、镜头校正提取不在范围内；锐化、清晰度和颗粒留给用户自行设置。

代码和原创文档采用 [MIT](../../LICENSE)。转换资源见 [许可说明](../../PROFILE_LICENSE.md)。四张 RAW 及衍生对比图**仅允许本项目测试和对比，其他用途需另行许可**，见[照片条款](../../samples/LICENSE.md)。RAW 通过单独的样本下载包提供，不塞进日常源码克隆。

欢迎 Issue 和 PR，见[贡献说明](CONTRIBUTING.md)。[赞助 b-z](https://github.com/sponsors/b-z)，入口启用取决于作者完成 GitHub Sponsors 开通。

对应英文文档版本：0.2.0。此项目独立开发，与 Nikon / Adobe 无官方合作关系。
