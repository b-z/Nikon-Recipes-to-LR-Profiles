# Nikon Recipes to LR Profiles

[English](../../README.md) · [日本語](../ja/README.md)

把尼康云创配方的色彩风格带进 Lightroom / Camera Raw，并使用 **0–200% 的数量滑块**调节强度。曝光、白平衡等后期操作仍可照常使用。

首发包含 **236 款尼康配方转换**，格式为基于 Adobe Standard 的增强配置文件 `.xmp`，无需额外 DCP 或安装包。目前实测机身是 **Nikon Z8**。这是通过 NX 真值标靶拟合的近似转换，不是把 NP3 滑块直接翻译成 LR，也不保证与尼康渲染完全一致。

1. 从 [Releases](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases) 下载并解压配置文件 ZIP。
2. 在 LR / Camera Raw 的配置文件浏览器中手动导入 `.xmp`；若未显示，重启 LR。
3. 打开 **Nikon Recipes LR 0.1** 分组，选择风格并调整数量。温和使用可以先试 30–50%，再调整曝光和白平衡。

[逐款评分与目录](../RECIPES.md) · [在线对比图库](https://nikon-recipes-to-lr-profiles.pages.dev/) · [网站构建](../../website/README.md) · [拟合流程](calibration.md) · [分数定义](metrics.md)

图库左侧展示所有配方的风景缩略图，两张风景图排在两张断层测试图前，不提供单独细节缩略图。NX 原版 JPEG 对照待补；接入后会生成[每张十六组的 NX/LR 对比拼图](../comparisons/README.md)。

**色彩断层是已知问题。** 19 款使用 YC7，其他 217 款沿用 YC4。此前 18 款 YC7 通过作者的 LR 实测，Bleach Blue 仍有残留断层；其余配置没有全部通过相同验收。低 ΔE 或低风险分不代表所有照片没有断层。对比图默认是 Adobe Standard 导出上的数学预览，不是 NX 真值；实际 Camera Raw 验证另行标记。

原始 NP3 请从作者或 [Nikon-Recipes](https://github.com/shouryan01/Nikon-Recipes) 获取，本仓库不打包原件。富士胶片模拟、镜头校正提取不在范围内；锐化、清晰度和颗粒留给用户自行设置。

代码和原创文档采用 [MIT](../../LICENSE)。转换资源见 [许可说明](../../PROFILE_LICENSE.md)。四张 RAW 及衍生对比图**仅允许本项目测试和对比，其他用途需另行许可**，见[照片条款](../../samples/LICENSE.md)。RAW 通过单独的样本下载包提供，不塞进日常源码克隆。

欢迎 Issue 和 PR，见[贡献说明](CONTRIBUTING.md)。[赞助 b-z](https://github.com/sponsors/b-z)，入口启用取决于作者完成 GitHub Sponsors 开通。

对应英文文档版本：0.1.0。此项目独立开发，与 Nikon / Adobe 无官方合作关系。文中的 Release 链接是计划发布位置，本地准备不等于已发布。
