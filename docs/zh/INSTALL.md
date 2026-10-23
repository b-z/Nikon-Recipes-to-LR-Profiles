## 安装与使用

236 款尼康云创配方的 Lightroom / Camera Raw 配置文件。在线对比并单独下载：https://nikon-recipes-to-lr-profiles.pages.dev/

### 安装

1. 解压本压缩包。
2. 打开配置文件浏览器，导入 `profiles/` 中的 `.xmp` 文件：
   - Lightroom Classic：「修改照片」模块的「基本」面板中，点击「配置文件」旁的四宫格图标，再点 **+** › **导入配置文件**。
   - Lightroom：**文件 › 导入配置文件和预设**。
   - Camera Raw：「编辑」面板中打开配置文件浏览器，点 **…** 菜单 › **导入配置文件和预设**。
3. 如果配置文件没有出现，请重启 Lightroom。不需要安装程序或单独的 DCP 文件。

### 使用

1. 在配置文件浏览器中，打开名称以 **Nikon Recipes LR 1.1** 开头的分组（每位配方作者一个分组），点击一款配方。
2. 用配置文件名称下方的「数量」滑块调整强度：100% 为原版配方色彩，30–50% 效果较温和，最高可到 200%。
3. 照常修图。曝光、白平衡、曲线等滑块都能正常使用。配置文件只包含配方的色彩和影调，配方中的锐化、中等锐化和清晰度不包含在内。

想让新照片按拍摄时使用的配方自动套用，见 https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/blob/main/docs/zh/auto-apply.md

如果某张照片看不到这些配置文件，说明压缩包与拍摄这张照片的相机不匹配。请下载对应机型的压缩包；其他相机请使用 `adobe` 通用版：https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest

### 注意事项

- 平滑的天空和焦外仍可能出现断层，数量越高越明显。欢迎在 https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues 反馈。
- `manifest.json` 列出了每个配置文件的作者和评分。
- 配方归各自的作者所有，每个配置文件中都有署名。本包不含原始 NP3 文件。配置文件采用 MIT 许可，并附 PROFILE_LICENSE.md 中的署名说明。
