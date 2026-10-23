# Nikon Recipes to LR Profiles

[![Latest release](https://img.shields.io/github/v/release/b-z/Nikon-Recipes-to-LR-Profiles)](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest) [![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/b-z)

[English](../../README.md) · [中文](../zh/README.md)

### 👉 [オンラインギャラリーを開く](https://nikon-recipes-to-lr-profiles.pages.dev/)：236 種類のレシピを NX Studio と比べて、気に入ったものだけダウンロード

[Nikon Imaging Cloud](https://imagingcloud.nikon.com/) では、プロの写真家が作成したカラーレシピが配信されています。ただし、レシピが反映されるのはカメラで記録される JPEG だけで、RAW 画像は変わりません。RAW を現像する場合、レシピを使う公式の方法はニコンの NX Studio だけで、多くの写真家のワークフローには合いません。

このプロジェクトは、レシピを **Lightroom と Photoshop Camera Raw** で再現します。プロファイルブラウザーでレシピを選び、「適用量」スライダー（0〜200%）で強さを調整するだけです。露光量、ホワイトバランス、トーンカーブなどの調整もこれまでどおり使えます。現在のリリースには **236 種類のレシピ**が含まれ、検証ではほとんどが元のレシピの色をよく再現しています。

[![4 枚のテスト写真での KG200P1。上段：NX Studio、下段：変換したプロファイルを使った Lightroom。](../images/kg200p1-comparison.jpg)](https://nikon-recipes-to-lr-profiles.pages.dev/#KG200P1)

*4 枚のテスト写真での KG200P1 レシピ。上段が NX Studio、下段が適用量 100% の Lightroom プロファイルです。[ギャラリーではすべてのレシピをこのように比較できます](https://nikon-recipes-to-lr-profiles.pages.dev/)。*

## インストール

1. [最新のリリース](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/releases/latest)から、お使いのカメラ用の ZIP をダウンロードして展開します。Camera Flexible Color のあるニコン機は `…-z8`、`-z9`、`-zf`、`-z6iii`、`-z5ii`、`-z50ii`、`-zr`、その他のカメラは `…-adobe` です。
2. Lightroom または Camera Raw のプロファイルブラウザーで「プロファイルを読み込み」を選び、`.xmp` ファイルを選択します。表示されない場合は Lightroom を再起動してください。
3. **Nikon Recipes LR 1.0** グループを開き、レシピを選んで強さ（適用量）を調整します。100% で元のレシピの色になり、30〜50% で控えめな効果になります。

機種別のパックは Camera Flexible Color をベースにしており、NX Studio に最も近くなります。Adobe パックは Adobe Standard ベースで、どのカメラでも使えます。パックの違いはベースプロファイルと対象機種だけです。詳しくは[インストールガイド](INSTALL.md)を参照してください。

## プロファイルに含まれるもの

プロファイルが再現するのはレシピの**色と階調**です。NX Studio が現像する色、コントラストとトーンカーブ、彩度、カラーグレーディングが含まれます。レシピの**輪郭強調、ミドルレンジシャープ、明瞭度は含まれず**、これらのディテール設定は無視されます。シャープ、テクスチャ、明瞭度、ノイズ軽減、粒子、周辺光量、レンズ補正はお使いの Lightroom の設定がそのまま使われます。

## 撮影時のレシピを自動で適用する

カメラは撮影時に使ったレシピの名前を NEF ごとに記録しています。このプロジェクトのコマンドラインツールはその名前を読み取り、RAW の横にサイドカーファイルを書き出します。Lightroom Classic や Camera Raw で開くと、対応するプロファイルがすでに適用された状態になります。

```sh
nikon-recipes-lr sidecars --profiles /path/to/nikon-recipes-lr-profiles-1.0.1-z8/profiles /path/to/photos
```

写真を読み込む前に実行してください。導入方法と詳細は[プロファイルの自動適用](auto-apply.md)を参照してください。

## レシピを比較する

- **[オンラインギャラリー](https://nikon-recipes-to-lr-profiles.pages.dev/)**：すべてのレシピを 4 枚の写真で表示し、NX Studio と Lightroom プロファイルを点滅で比較できます。2 つのスコアと、レシピごとのダウンロードボタンもあります。
- **[レシピカタログ](../RECIPES.md)**：各プロファイルの作者、NX Studio との色差、段差リスクのスコア（[スコアの説明](metrics.md)）。

## 仕組み

### レシピを測る

基準は NX Studio です。ニコン自身が RAW ファイルにレシピを適用する方法だからです。レシピごとに、NX Studio で合成テストチャートを現像します。これは 24,720 色のパッチを並べた Z 8 の RAW ファイルで、暗部から明部、無彩色から高彩度まで、あらゆる色相の色を含みます。同じチャートを Camera Raw でも、レシピなしのベースプロファイルで現像します。各パッチから、Lightroom の出発点となる色と、レシピがそれを変えた色の組が 1 つ得られます。レシピの設定を 1 項目ずつ翻訳することはしません。ニコンのトーンカーブ、カラーブレンダー、カラーグレーディングは、Lightroom のスライダーとは色空間も処理の順番も異なるからです。プロファイルは NX Studio が実際に出力した結果に従います。

### 滑らかな色変換を求める

24,720 組の色から、任意の Lightroom の色をレシピの色に変換する関数を求めます。Lightroom のカラーテーブルは 3 つの軸それぞれに 32 点、合計約 3.3 万点（各 3 つの値）を持ち、点と点の間は直線で補間されます。各点を自由に合わせると、テーブルはパッチごとのわずかな測定誤差に引っ張られ、隣り合うマス目ごとに少しずつ違う方向に折れ曲がります。写真では、空、肌、ボケた背景など色がゆっくり変わる場所で、この折れ目が目に見える段差（バンディング）になります。このプロジェクトの初期のバージョンでも実際に起きました。

0.2 以降、変換は**滑らかな 3 次スプライン**です。各軸 16 個の制御点を持ち、曲率にペナルティをかけています。1 階と 2 階の導関数がどこでも連続なのでグラデーションは滑らかに保たれ、係数に上限と下限があるので出力は常に色空間の内側に収まり、クリップしません。32³ のテーブルはこの滑らかな関数からサンプリングします。代償はチャート上の差がわずかに大きくなることですが、1.0 の NX Studio との色差の中央値は約 0.5 ΔE で、ほとんどの人が見分けられない程度です。[手法の説明（英語）](../Y8_REBUILD.md)。

### Lightroom のプロファイルとして保存する

レシピごとに、Adobe の**拡張プロファイル**を 1 つ作ります。Lightroom Classic、Lightroom、Camera Raw がそのまま読み込める小さな `.xmp` ファイルで、Adobe 自身のクリエイティブプロファイルと同じ形式です。主なフィールドは次のとおりです。

- `crs:PresetType="Look"`：ベースプロファイルの上に重ねるプロファイルであることを示します。
- `crs:CameraProfile`：ベースプロファイル。機種別のパックは `Camera Flexible Color`、Adobe パックは `Adobe Standard` です。Camera Raw はまずこれで RAW を現像します。
- `crs:RGBTable` と `crs:Table_<ID>`：32×32×32 のカラーテーブル。16 ビットの値を「変化なし」からの差として保存し、圧縮してテキストにしています。ID はテーブルのチェックサムです。Camera Raw はベースプロファイルの後に、これをすべてのピクセルに適用します。
- `crs:SupportsAmount="True"` と、テーブルのヘッダーにある 200% の上限：これによってプロファイルに**適用量**スライダーが付き、ベースプロファイル（0%）から完全なレシピ（100%）、さらにその先までを混ぜ合わせます。
- `crs:CameraModelRestriction`（例：`Nikon Z f`）、`crs:Group`、`crs:Name`、`crs:UUID`：プロファイルがどこに、どの名前で表示されるかを決めます。リリースごとに UUID を新しくしているので、リリース同士が上書きし合うことはありません。

Lightroom で完全な 3D カラーテーブルを持てるのはプロファイルだけです。現像プリセットは HSL やトーンカーブなどのスライダーを設定できるだけで、レシピがすべての色をどう動かすかは表現できず、自分のスライダー設定も上書きしてしまいます。カメラプロファイル（DCP）はカメラごとに作る必要があり、適用量スライダーもありません。拡張プロファイルなら、レシピはプロファイルブラウザーの選択肢の 1 つになり、強さを調整でき、ほかのスライダーはすべて自由に使えます。

### Camera Flexible Color を使う理由

0.2 までのプロファイルは Adobe Standard をベースにしていました。Camera Raw は Adobe Standard の黒レベルを写真ごとに最も暗いピクセルに応じて下げるため、真っ黒な部分のない日中の写真では、シャドウが NX Studio より暗く、色が濃くなっていました。Camera Flexible Color は、レシピの土台であるニコンのピクチャーコントロール「Flexible Color」に合わせた Adobe のプロファイルで、センサーの黒レベルを保ちます。これに切り替えたことで、1.0 はチャート上で 236 種類すべてが 0.2 より NX Studio に近くなり、実際の写真のシャドウも NX Studio にずっと近づきました。段差リスクのスコアも 235 種類で下がっています。[詳細（英語）](../Y9_FLEX_BASE.md)。

Adobe のカメラマッチングプロファイル（カメラスタンダード、カメラニュートラルなど）はどれもセンサーの黒レベルを保つので、どれを使ってもシャドウの問題は解決します。Camera Flexible Color を選んだのは、それがレシピの出発点だからです。イメージングレシピはニコンのピクチャーコントロール「Flexible Color」をもとに作られています。Adobe によるその再現から始めれば、カラーテーブルはレシピ自身の変更だけを表せばよく、最小の、つまり最も滑らかな補正になります。Adobe は Flexible Color を持つニコン機（Z 8、Z 9、Z f、Z6III、Z5II、Z50II、ZR）ごとに Camera Flexible Color を用意し、その機種でのニコンの現像に合わせているため、同じテーブルをそのまま使えます。プロファイルは 1 機種にしか限定できないので、機種ごとにパックを分けています。Z f と Z6III のサンプル RAW では、機種別のパックのほうが Adobe パックより NX Studio に近くなりました。

## 自分のレシピを変換する

自作のピクチャーコントロールや、リリースに含まれていないレシピも変換できます。リポジトリにはチャート、NX Studio の設定、Camera Raw の測定値をまとめた [Z 8 キャリブレーションキット](../../calibration/z8/)があり、NX Studio と Python があれば 1 レシピ数分で変換できます。[自分のレシピを変換する](convert-your-own-recipe.md)を参照してください。

## 既知の制限

- **段差（バンディング）。** 滑らかな空やボケでは、特に適用量が高いときに段差が出ることがあります。見つけた場合は、レシピ名と小さな切り抜きを添えて[報告](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues/new/choose)してください。
- **近似。** 236 種類のうち 223 種類で、NX Studio との平均色差がチャート上で 1 ΔE（CIEDE2000、人が気づく最小の差の目安）未満、最大は 1.44 ΔE です。個々の色や写真ではもっと差が出ることがあります。

## 貢献

他のニコン機の校正、再現できる段差の報告、より良いフィッティング手法、テスト、ドキュメントや翻訳を歓迎します。まず[貢献ガイド](CONTRIBUTING.md)を読み、[行動規範](../../CODE_OF_CONDUCT.md)に従ってください。リリースごとの変更は [CHANGELOG](../../CHANGELOG.md) にあります。

## プロジェクトを支援する

このプロジェクトは空き時間に保守しています。プロファイルが役に立ったら、[GitHub Sponsors](https://github.com/sponsors/b-z) や WeChat で支援していただけるとうれしいです。支援は任意で、Issue やプルリクエストの扱いには影響しません。

<table><tr>
<td align="center" valign="middle"><a href="https://github.com/sponsors/b-z"><img src="https://img.shields.io/badge/GitHub%20Sponsors-%E2%9D%A4%20Sponsor-db61a2?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Sponsor on GitHub" height="36"></a></td>
<td align="center" valign="middle"><img src="../images/wechat-reward.jpg" alt="WeChat の投げ銭用 QR コード" width="180"></td>
</tr></table>

## クレジットとライセンス

- レシピの権利は各作者にあり、すべてのプロファイル、カタログ、[オンラインギャラリー](https://nikon-recipes-to-lr-profiles.pages.dev/)に作者を記載しています。元の NP3 ファイルは再配布していません。作者、Nikon Imaging Cloud、または [Nikon-Recipes アーカイブ](https://github.com/shouryan01/Nikon-Recipes)から入手してください。
- コードとドキュメントは [MIT](../../LICENSE)、生成したプロファイルは MIT と [PROFILE_LICENSE](../../PROFILE_LICENSE.md) の表示条件に従います。第三者に関する表示は [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md) にあります。
- 4 枚のサンプル写真、キャリブレーション用チャート（埋め込みプレビューはそのうちの 1 枚）、およびそこから作った画像は MIT ライセンス**ではありません**。このプロジェクトのテストと比較にのみ使用できます。[写真の利用条件](../../samples/LICENSE.md)を参照してください。

これは独立したコミュニティプロジェクトで、ニコンや Adobe とは提携しておらず、承認も受けていません。
