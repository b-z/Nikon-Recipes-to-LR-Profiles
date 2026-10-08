# Nikon Recipes to LR Profiles

[English](../../README.md) · [中文](../zh/README.md)

ニコンのイメージングレシピの色調を Lightroom / Camera Raw で使い、**適用量を 0〜200%** で調整できます。露光量やホワイトバランスなどの RAW 編集を続けられます。

初回パックには **236 種類のニコンレシピ変換**を収録します。Adobe Standard をベースとする拡張プロファイル `.xmp` で、別の DCP やインストーラーは不要です。動作確認したカメラは **Nikon Z8** です。NX Studio のチャート出力から校正した近似であり、NP3 スライダーの直接変換でも、ニコン出力との完全一致でもありません。

1. [Releases](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases) からプロファイル ZIP を取得し、展開します。
2. LR / Camera Raw のプロファイルブラウザーで `.xmp` を読み込みます。表示されない場合は LR を再起動します。
3. **Nikon Recipes LR 0.1** グループを開き、適用量を調整します。控えめに使う場合は 30〜50% から試し、露光量と WB を編集します。

[レシピ一覧とスコア](../RECIPES.md) · [オンラインギャラリー](https://nikon-recipes-to-lr-profiles.pages.dev/) · [サイトのビルド](../../website/README.md) · [校正手順](calibration.md) · [スコアの定義](metrics.md)

左のサイドバーには各レシピの風景サムネイルを表示し、風景写真 2 枚、色の段差テスト 2 枚の順に並べます。別の詳細サムネイルはありません。NX 原版 JPEG の比較画像は準備中です。取り込み後、[16 レシピずつの NX/LR 比較シート](../comparisons/README.md)を生成します。

**色の段差は既知の問題です。** 19 種は YC7、残る 217 種は YC4 です。以前の Lightroom 評価では YC7 の 18 種が許容されましたが、Bleach Blue には段差が残りました。残りをすべて同じ条件で確認したわけではありません。低い ΔE やリスクスコアは、すべての写真で段差がないことを保証しません。通常の比較画像は Adobe Standard 出力にテーブルを適用した数値プレビューで、NX の正解画像ではありません。実際の Camera Raw 検証は別に表示します。

元の NP3 は作者または [Nikon-Recipes](https://github.com/shouryan01/Nikon-Recipes) から入手してください。本プロジェクトは元ファイルを同梱しません。富士フイルムシミュレーション変換、レンズ補正抽出は対象外です。シャープ、明瞭度、粒子はユーザー側で調整してください。

コードと独自ドキュメントは [MIT](../../LICENSE)、変換リソースは[別の説明](../../PROFILE_LICENSE.md)を参照してください。4 枚の RAW と派生画像は**本プロジェクトのテスト・比較に限って利用可能**で、その他の利用には許可が必要です。[写真の条件](../../samples/LICENSE.md)を確認してください。RAW はソースの通常の clone ではなく、独立したサンプル ZIP で配布します。

Issue と PR を歓迎します。[貢献方法](CONTRIBUTING.md) · [b-z を支援](https://github.com/sponsors/b-z)（GitHub Sponsors の有効化後に利用できます）。英語文書の対応バージョン：0.1.0。Nikon / Adobe の公式プロジェクトではありません。Release リンクは公開予定先です。
