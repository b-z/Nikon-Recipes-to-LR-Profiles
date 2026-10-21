# 参与贡献

感谢你的帮助！完整指南见[英文版 CONTRIBUTING](../../CONTRIBUTING.md)，以英文版为准。Issue 和 PR 建议用英文，以便所有人都能参与；用中文或日文反馈问题也完全没问题。参与本项目即表示同意遵守[行为准则](../../CODE_OF_CONDUCT.md)。

**可以帮忙的方向**

- 用[问题表单](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose)反馈断层或偏色：写明配方、版本、数量、相机和 Lightroom 版本，附上可以公开的小裁切。
- 校准其他机身（目前只有 Nikon Z 8），见[校准说明](../en/calibration.md)。
- 改进拟合方法、断层指标或感知评估；改进代码、测试、网站和翻译。

**开发环境**（Python 3.10+）

```sh
python -m pip install -e ".[dev]"
ruff format src tests scripts website/scripts
ruff check src tests scripts website/scripts
python -m pytest
```

**PR 要求**：一次只做一件事并附测试；改动色彩或断层时写明拟合数据与评估数据，附 `audit` 结果，说明是否在 Lightroom / Camera Raw 中实际检查过。仅凭标靶 ΔE 或单张照片不能宣称消除了断层。不接受原始 NP3 合集、Adobe SDK、Adobe 基础配置文件或无权分享的照片。

贡献按项目的 [MIT 许可](../../LICENSE)提供，无需另签协议。
