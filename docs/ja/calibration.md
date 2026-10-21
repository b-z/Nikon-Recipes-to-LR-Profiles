# 校正手順

同じ合成 RAW を使い、NX と Adobe から元の寸法で 16 ビット Adobe RGB TIFF を出力します。ADL、ノイズ低減、シャープ、明瞭度と無効化可能な光学補正を切ります。Adobe Standard、撮影時 WB、線形ユーザーカーブ、基本調整ゼロを基準にします。無効化できない設定は記録してください。

1. 校正済みの Z8 donor からチャートを作るか、既存のチャートとパッチ中心のメタデータを用意します。`make-target` は実験機能です。同じ機種名でも黒レベル、WB、Bayer 配列の互換性は保証されません。[英語の条件](../en/calibration.md)を確認してください。埋め込みプレビューは donor の元画像のままなので RAW レンダーを確認します。
2. NX で設定済み `.nksc` テンプレートを保存し、`prepare-nx --source chart.NEF --template chart.NEF.nksc --recipes recipe.NP3 --output nx-batch` でバッチを作ります。他の設定は自動検証されないので NX 画面で確認して出力します。
3. `sample` で TIFF を採取し、`fit --adobe-samples adobe.json --nx-samples nx.json --name "Recipe" --author "Author" --output recipe.xmp` でフィットし、`audit recipe.xmp` で監査します。既定ではリリース版と同じ滑らかなスプライン方式（`--method spline`）を使い、新しいプロファイルは `Nikon Recipes LR/Custom` グループに入ります（`--group` で変更可）。詳しい引数は英語文書を参照してください。
4. 手動で読み込み、必要なら LR を再起動します。複数の実写真と平滑な色経路を使って 100% / 200% でも検証します。CLI のスコアは学習チャートの結果で、独立検証には別データが必要です。

Python 核心はクロスプラットフォームです。Adobe 自動出力は macOS、Photoshop、ExifTool が必要で、プロファイルの自動インストールや Photoshop の再起動は行いません。出力先は明示指定し、一時 RAW/TIFF は処理後に削除します。

適用量はテーブルの RGB 空間で混合し、完成 JPEG のバイト単位混合や Nikon の各スライダーの比例縮小ではありません。プロファイルを変えると露光量や WB の操作感も変わり得ます。センサー段階のクリップは回復できません。シャープ、粒子、レンズ補正の変換は対象外です。

英語文書の対応バージョン：0.2.0。
