# Nikon Recipes to LR Profiles

[English](../../README.md) · [中文](../zh/README.md)

Nikon Imaging Cloud の **イメージングレシピ** の色調を Lightroom / Camera Raw で使い、**適用量を 0〜200%** で調整できます。露光量やホワイトバランスなどの RAW 編集はそのまま使えます。

現在のリリースには **236 種類のレシピ変換** を収録しています。Adobe Standard をベースとする拡張プロファイル `.xmp` で、DCP やインストーラーは不要です。各プロファイルは NX Studio の出力に合わせて校正した近似であり、ニコンの現像エンジンでも、NP3 スライダーの直接変換でもありません。

## プロファイルを使う

1. [最新リリース](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest) から `nikon-recipes-lr-profiles-<バージョン>.zip` をダウンロードして展開します。
2. Lightroom または Camera Raw のプロファイルブラウザーで「プロファイルを読み込み」を選び、`profiles/` の `.xmp` を指定します。表示されない場合は Lightroom を再起動します。
3. **Nikon Recipes LR 0.2** グループからルックを選び、適用量を調整します。控えめにするなら 30〜50% から試してください。

新しいリリースはグループと ID が別なので、旧版と併用できます。不要になったら旧グループを削除してください。詳しくは[インストール手順](INSTALL.md)を参照してください。

## レシピを比較する

- **[オンラインギャラリー](https://nikon-recipes-to-lr-profiles.pages.dev/)**：各レシピを 4 枚の写真で表示し、NX Studio と LR 変換を並べて比較できます（A/B 切り替え、個別ダウンロード付き）。
- **[レシピ一覧](../RECIPES.md)**：作者クレジット、フィット誤差、段差リスクスコア（[スコアの説明](metrics.md)）。

## 仕組み

1. 約 24,000 色のパッチを含む合成チャート RAW を、NX Studio（レシピ適用）と Camera Raw（Adobe Standard）でそれぞれ現像します。
2. Adobe の色から NX の色への、滑らかで範囲内に収まる 3D 色変換を当てはめます。0.2.0 以降は軸あたり 16 制御点の 3 次スプラインを使い（[方法の説明](../Y8_REBUILD.md)）、テーブルを直接当てはめるより階調が滑らかになります。
3. 変換は 32³ RGB テーブルとして、Adobe Standard 上の Lightroom「ルック」プロファイルに格納されます。適用量スライダーで元画像と混ぜ合わせます。

NP3 ファイルからはレシピ名などのメタデータのみを読み取り、色は NX Studio の実際の出力から得ています。

## 既知の制限

- **色の段差。** 滑らかな空やボケでは、特に適用量が高いと段差が出ることがあります。前版で段差があった 58 種は複数の写真で再確認し、段差は見られませんでした。残る 178 種は個別には確認していません。見つけた場合は[報告](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose)してください。
- **カメラ。** 校正・検証済みは Nikon Z 8 のみです。他の機種では結果が異なる場合があります。
- **対象範囲。** 色と全体の階調のみを再現します。シャープ、明瞭度、粒子、周辺光量、レンズ補正は Lightroom 側で設定してください。
- **近似。** 236 種中 197 種で NX Studio との平均チャート色差が 1 ΔE（CIEDE2000）未満、最大 1.85 ΔE です。個々の色や写真ではより大きく異なることがあります。

## 自分でレシピを校正する

同じチャートを NX Studio と Camera Raw で現像した結果が必要です。手順は[校正ガイド](calibration.md)（詳細は[英語版](../en/calibration.md)）、コマンド例は[英語の README](../../README.md#calibrate-a-recipe-yourself) を参照してください。

## 貢献

他のニコン機の校正、再現可能な段差の報告、より滑らかなフィット手法、テスト、翻訳を歓迎します。[貢献ガイド](CONTRIBUTING.md)と[行動規範](../../CODE_OF_CONDUCT.md)をお読みください。変更履歴は [CHANGELOG](../../CHANGELOG.md) にあります。

## サポート

プロファイルが役に立った場合は、[GitHub Sponsors](https://github.com/sponsors/b-z) からプロジェクトを支援できます。支援は任意で、Issue や PR の扱いには影響しません。

## クレジットとライセンス

- レシピの権利は各作者にあり、すべてのプロファイルと一覧に作者を記載しています。元の NP3 ファイルは再配布していません。作者、Nikon Imaging Cloud、または [Nikon-Recipes アーカイブ](https://github.com/shouryan01/Nikon-Recipes)から入手してください。
- コードとドキュメントは [MIT](../../LICENSE)、生成プロファイルは MIT と[帰属表示の注意](../../PROFILE_LICENSE.md)に従います。第三者に関する注意は [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md) にあります。
- 4 枚のサンプル写真とその派生画像は MIT の対象**外**で、本プロジェクトのテストと比較にのみ使用できます。[写真の条件](../../samples/LICENSE.md)を参照してください。

本プロジェクトは独立したコミュニティプロジェクトであり、Nikon および Adobe とは関係がなく、承認も受けていません。
