# 貢献ガイド

ご協力ありがとうございます。詳しいガイドは[英語版 CONTRIBUTING](../../CONTRIBUTING.md) を正とします。Issue と PR は誰もが読めるよう英語を推奨しますが、日本語や中国語での報告も歓迎します。参加にあたっては[行動規範](../../CODE_OF_CONDUCT.md)に従ってください。

**協力できること**

- [Issue フォーム](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose)で段差や色ずれを報告する（レシピ、バージョン、適用量、カメラ、Lightroom のバージョン、共有可能な小さな切り抜き）。
- 他の機種を校正する（現在は Nikon Z 8 のみ）。[校正ガイド](../en/calibration.md)を参照してください。
- 新しいレシピを変換する。[Z 8 キャリブレーションキット](../../calibration/z8/)があれば NX Studio と Python だけでできます（[ガイド](convert-your-own-recipe.md)）。プロファイルを送る前に、レシピとその作者を書いた Issue を作成してください。
- フィット手法、段差の指標、知覚的な評価、コード、テスト、ウェブサイト、翻訳の改善。

**開発環境**（Python 3.10 以上）

```sh
python -m pip install -e ".[dev]"
ruff format src tests scripts website/scripts
ruff check src tests scripts website/scripts
python -m pytest
```

**PR の条件**：1 つの変更に絞り、テストを付けてください。色や段差に関わる変更では、フィットに使ったデータと評価に使ったデータ、`audit` の結果、Lightroom / Camera Raw で実際に確認したかを記載してください。チャート ΔE や 1 枚の写真だけで段差の解消とは言えません。元の NP3 コレクション、Adobe SDK、Adobe のベースプロファイル、共有する権利のない写真は受け付けられません。

貢献はプロジェクトの [MIT ライセンス](../../LICENSE)で提供されます。別途の契約は不要です。
