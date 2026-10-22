# 校准流程

使用同一张合成 RAW，NX 和 Adobe 都导出原尺寸的 16 位 Adobe RGB TIFF。关闭 ADL、降噪、锐化、清晰度和可关闭的光学校正。Adobe 基准用 Adobe Standard、拍摄时白平衡、线性用户曲线、基础参数归零。无法关闭的项目要记录。

1. 使用自己的已校准 Z8 donor 生成标靶，或提供已有标靶与色块中心元数据。`make-target` 是实验功能，机身型号相同并不表示黑电平、白平衡和 Bayer 布局兼容；必须按[英文指南](../en/calibration.md)确认。嵌入缩略图仍是 donor 原图，检查 RAW 渲染。
2. NX 保存一个配置正确的 `.nksc` 模板，用 `prepare-nx --source chart.NEF --template chart.NEF.nksc --recipes recipe.NP3 --output nx-batch` 创建批次。注入配方不会替你验证其他设置，在 NX 面板中核对后导出。
3. 用 `sample` 从 TIFF 采样；用 `fit --adobe-samples adobe.json --nx-samples nx.json --name "Recipe" --author "Author" --output recipe.xmp` 拟合，再用 `audit recipe.xmp` 审计。默认使用与发布版相同的平滑样条方法（`--method spline`），新配置文件放在 `Nikon Recipes LR/Custom` 分组（可用 `--group` 修改）。完整参数见英文指南。
4. 手动导入并重启 LR，在多张真实照片、平滑色路、100% 与 200% 强度下检查。拟合报告是训练标靶分数，独立验证需另设数据。

Python 核心可跨平台；自动 Adobe 渲染需要 macOS、Photoshop 与 ExifTool，不会自动装配置文件或重启 Photoshop。用户指定输出目录，临时本地 RAW/TIFF 用完即删。

数量在颜色表工作空间中混合，不等于把两张成品 JPEG 逐字节混合，也不等于每个尼康滑块乘一个比例。改变配置文件会影响曝光和白平衡滑块手感；已在传感器阶段剪裁的高光无法恢复。锐化、颗粒与镜头校正不是本项目转换目标。

Nikon Z 8 用户可以直接使用仓库中的 [Z 8 校准包](../../calibration/z8/)，见[转换你自己的配方](convert-your-own-recipe.md)；本页面向其他机身。
