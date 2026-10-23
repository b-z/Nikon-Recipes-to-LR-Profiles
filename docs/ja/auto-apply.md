# プロファイルの自動適用

[English](../en/auto-apply.md) · [中文](../zh/auto-apply.md)

ニコンのカメラは撮影時に、使用中のピクチャーコントロールの名前を NEF に記録します。イメージングレシピの場合はレシピ自身の名前（例：`KP160`）です。`nikon-recipes-lr sidecars` コマンドはこの名前を読み取り、対応するプロファイルを選択する XMP サイドカー（`_DSC1234.xmp` など）を各 NEF の横に書き出します。Lightroom Classic と Camera Raw はサイドカーを読み込むので、写真はレシピが適用された状態で開きます。プロファイルはほかの補正と同じように変更・解除できます。

## 必要なもの

- 展開したリリースのプロファイル（Lightroom に読み込んだものと同じファイル）。
- Python 3.10 以降と、このプロジェクトのツール：

  ```sh
  python -m pip install "git+https://github.com/b-z/Nikon-Recipes-to-LR-Profiles.git"
  ```

- カメラの情報を読み取る [ExifTool](https://exiftool.org/)（macOS で Homebrew を使う場合：`brew install exiftool`）。

## 手順

1. いつも読み込み前にしているように、カードから写真をフォルダーにコピーします。
2. まず何も書き込まずに結果を確認します：

   ```sh
   nikon-recipes-lr sidecars --dry-run --profiles ~/Downloads/nikon-recipes-lr-profiles-1.1.0-z8/profiles ~/Pictures/2026-10-18
   ```

   `written` にはサイドカーが書き出される写真と、それぞれのプロファイルが表示されます。`no_profile` は、対応するプロファイルのないピクチャーコントロール（スタンダードなど）で撮った写真の数です。
3. `--dry-run` を外して同じコマンドを実行します。
4. フォルダーを Lightroom Classic に読み込みます。Camera Raw（Photoshop や Bridge）では、ファイルを開くとサイドカーが読み込まれます。

サブフォルダーも対象にするには `--recursive`、適用量を 100% ではなく 50% から始めるには `--amount 0.5` を付けます。

**すでに読み込んだ場合：** フォルダーに対してコマンドを実行してから、Lightroom Classic で写真を選択し、「メタデータ › ファイルからメタデータを読み込み」を選びます。これらの写真の現像設定がサイドカーの内容に置き換わるので、編集を始める前に行ってください。

## サイドカーの内容

- 選んだ適用量でのレシピのプロファイルと、そのベースプロファイル（機種別のパックは Camera Flexible Color、Adobe パックは Adobe Standard）。
- Camera Raw が新しい写真に適用するのと同様に、レンズプロファイル補正をオン。

それ以外の設定は含まれず、Camera Raw の初期値が使われます。サイドカーのある写真には、独自に設定した RAW 初期設定は適用されません。プリセットを使っている場合は読み込み後に適用してください。プロファイルを含むプリセットは、レシピのプロファイルを置き換えます。

## 対応づけのルール

- **リリースのプロファイル**はファイル名で識別し、各レシピのピクチャーコントロール名は NP3 ファイルから取得しています。236 個の名前はすべて異なるので、1 枚の写真が 2 つのレシピに対応することはありません。
- **自分で変換したプロファイル**（[自分のレシピを変換する](convert-your-own-recipe.md)）はプロファイル名で対応づけます。フィッティング時に、カメラに表示されるピクチャーコントロール名を `--name` に指定してください。
- すでにサイドカーがある写真はスキップします。`--overwrite` を付けるとサイドカーを置き換え、そこに保存されていた編集は失われます。
- 読み取るのは `.NEF` と `.NRW` だけで、元のファイルは変更しません。

このコマンドは Lightroom Classic と Camera Raw で確認済みです。クラウド版 Lightroom での結果は [Issues](https://github.com/b-z/Nikon-Recipes-to-LR-Profiles/issues) でお知らせください。
