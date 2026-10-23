# 自分のレシピを変換する

[English](../en/convert-your-own-recipe.md) · [中文](../zh/convert-your-own-recipe.md)

`.NP3` ファイルとして保存したピクチャーコントロールやイメージングレシピは、自作のものも含めて Lightroom のプロファイルに変換できます。ツールは、レシピを適用した NX Studio がカラーチャートをどう現像するかを測り、それに合わせてプロファイルを作ります。リリースのプロファイルと同じ方法です。準備ができれば、1 レシピ数分で終わります。

## 必要なもの

- **`.NP3` ファイルのレシピ。** カメラで「写真撮影メニュー › カスタムピクチャーコントロール › メモリーカードを使用 › メモリーカードにコピー」を選ぶと、カードの `NIKON/CUSTOMPC` フォルダーに書き出されます。レシピの作者が NP3 ファイルを直接配布していることもよくあります。
- **[NX Studio](https://imaging.nikon.com/imaging/lineup/software/nx_studio/)**：ニコンの無料 RAW ソフト（macOS / Windows）。
- **Python 3.10 以降。**
- **このリポジトリ**：ツールと [Z 8 キャリブレーションキット](../../calibration/z8/)（チャートの RAW、パッチの位置、NX Studio の設定、対応する Camera Raw の測定値）が入っています。Lightroom や Photoshop で何かを現像する必要はありません。

```sh
git clone https://github.com/b-z/Nikon-Recipes-to-LR-Profiles.git
cd Nikon-Recipes-to-LR-Profiles
python -m pip install -e .
unzip calibration/z8/chart.NEF.zip -d calibration/z8
```

以下の例はリポジトリのフォルダーで実行し、レシピが `MyRecipe.NP3` であるものとします。

## 1. NX Studio 用にチャートを準備する

```sh
nikon-recipes-lr prepare-nx --source calibration/z8/chart.NEF --template calibration/z8/nx-template.nksc \
  --recipes MyRecipe.NP3 --output nx-batch
```

レシピを適用する NX Studio の設定付きで `nx-batch/MyRecipe.NEF` が作られます。複数の `.NP3` ファイルを一度に指定することもできます。

## 2. NX Studio からチャートを書き出す

1. NX Studio で `nx-batch` フォルダーを開き、チャートを選択します。調整パネルのピクチャーコントロールに自分のレシピが表示されているはずです。
2. 「書き出し」を選び、形式を **TIFF（16 ビット）** にして元のサイズのまま、`MyRecipe.TIF` を NEF の横に保存します。キットの設定はすでに Adobe RGB 色空間になっています。

チャートは色の帯が並んだ画像です。サムネイルにはチャートの元になった写真が表示されることがありますが、無視してかまいません。

## 3. 測定とフィッティング

```sh
nikon-recipes-lr sample nx-batch/MyRecipe.TIF --metadata calibration/z8/chart.json --output MyRecipe-nx.json
nikon-recipes-lr fit --adobe-samples calibration/z8/camera-flexible-color.npy --base "Camera Flexible Color" \
  --nx-samples MyRecipe-nx.json --name "MyRecipe" --author "あなたの名前" \
  --output MyRecipe.xmp --report MyRecipe-report.json
nikon-recipes-lr audit MyRecipe.xmp
```

- TIFF がチャートと同じサイズの 16 ビット Adobe RGB でない場合、`sample` はメッセージを出して止まります。
- 出力の `mean_de` は、チャート上での NX Studio との平均色差です。1 未満なら見分けるのは困難です。リリースのプロファイルはおよそ 0.1〜1.4 です。
- `audit` は段差リスクのスコアを表示します（[スコアの説明](metrics.md)）。
- [`sidecars`](auto-apply.md) で自動適用したい場合は、カメラに表示されるピクチャーコントロール名を `--name` に指定してください。

これでリリースの機種別パックと同じ、Camera Flexible Color ベースで Z 8 に限定したプロファイルができます（他の機種ではその機種のキットを使います。[後述](#他の機種と自作のチャート)を参照）。Adobe パックのように Adobe Standard ベースでどのカメラでも表示されるプロファイルにしたい場合は、Adobe Standard の測定値を使い、機種の制限を外します。

```sh
nikon-recipes-lr fit --adobe-samples calibration/z8/adobe-standard.npy --camera "" \
  --nx-samples MyRecipe-nx.json --name "MyRecipe" --author "あなたの名前" --output MyRecipe-any-camera.xmp
```

フィッティングは数秒で終わります。キットでリリースのレシピをこの方法で作り直すと、公開中のプロファイルとの差は平均 0.1 ΔE ほどです。

## 4. Lightroom で使う

プロファイルブラウザーの「プロファイルを読み込み」で `MyRecipe.xmp` を読み込むと、**NRLR - Custom** グループに表示されます。本格的に使う前に、滑らかな空やボケのある写真で、適用量 100% とそれ以上で確認してください。リリースのプロファイルと同じく、再現するのは色と階調だけで、レシピの輪郭強調、ミドルレンジシャープ、明瞭度は含まれません。

## 他の機種と自作のチャート

リリースでフィットした各機種のキットがリポジトリにあります：[Z 8](../../calibration/z8/)、[Z 9](../../calibration/z9/)、[Z f](../../calibration/zf/)、[Z50II](../../calibration/z50ii/)、[Z6III](../../calibration/z6iii/)、[Z5II](../../calibration/z5ii/)。Camera Raw と NX Studio では機種ごとの明るさの扱いが完全には一致しないため、他の機種ではその機種のキットを使ってください。`prepare-nx` にはその `chart.NEF`、`sample` には `chart.json`、`fit` には `camera-flexible-color.npy` を使い、`--camera` には Camera Raw での機種名（例：`"Nikon Z f"`。機種名は `src/nikon_recipes_lr/cameras.py` にあります）を指定します。Z6III と Z5II のキットにはチャートの RAW が含まれていません。自分の写真から作る方法はそれぞれの README にあります。

キットのない機種（ZR など）は、[`scripts/make_chart.py`](../../scripts/make_chart.py) でその機種のロスレス圧縮または非圧縮の NEF からチャートを作り、NX Studio と Camera Raw で一度ずつ現像して、Camera Raw の現像結果を `sample` で測定します。背景は[キャリブレーションの流れ](calibration.md)（完全版は[英語](../en/calibration.md)）にあります。他機種のキットの貢献を歓迎します。
