# Qwen-Image-2.1 ローカル実行

AMD Radeon 8060S（gfx1151）、ROCm版PyTorchを使う環境です。
導入・検証の状況は [PROGRESS.md](PROGRESS.md) を参照してください。

## 画像生成

このディレクトリで実行します。モデルは `models/Qwen-Image-2.1` に保存しています。

```bash
.venv/bin/python generate.py \
  --prompt 'A small red fox sitting in a peaceful green forest, soft morning sunlight, detailed natural photography.' \
  --size 512 --steps 20 --seed 42 \
  --output outputs/first-image.png
```

BF16とモデル単位のCPUオフロードを使います。モデルの読み込みはローカルファイルのみです。
GPUデバイスにアクセスできるホスト環境で実行してください。
PNGと同じ名前のJSONに、プロンプト、設定、所要時間、PyTorchが計測したGPUメモリのピークを記録します。
512×512・20ステップは初回の動作確認用設定です。

### テキストファイルからプロンプトを入力

UTF-8で保存したテキストファイルを `--prompt-file` に指定できます。

```bash
.venv/bin/python generate.py --prompt-file prompt.txt --output outputs/from-file.png
```

ファイル全体を1つのプロンプトとして読み込みます。日本語と複数行に対応し、
先頭・末尾の空白や改行は除去します。`--prompt` との同時指定はできません。
ファイルが読めない場合や内容が空の場合は、モデルの読み込み前にエラーを表示します。
出力JSONにはファイル名と実際に読み込んだプロンプトを記録します。

### 画像を入力して編集・合成する

1枚の画像は `--image` で指定します。繰り返し指定もできます。

```bash
.venv/bin/python generate.py --image input.png \
  --prompt 'Change the background to a sunset beach.' --output outputs/edit.png
```

複数画像は `--imagefile` の後ろにパスを並べて指定します。

```bash
.venv/bin/python generate.py --imagefile delorean.jpg race.jpg \
  --prompt-file prompt.txt --output outputs/composite.png
```

例えば `prompt.txt` には「画像1のデロリアンが、画像2の競馬レースで馬群の先頭を走る場面にしてください。光、影、遠近感を自然に合わせてください。」と記述します。

`--image delorean.jpg --image race.jpg` も同じ指定です。両オプションの併用も可能で、
コマンドに指定した順に最大10枚を渡します。`--imagefile` は画像パスのリストを直接受け取るもので、
ファイル一覧を書いたテキストファイルを読むオプションではありません。
パスに空白がある場合は引用符で囲んでください。

画像の向きはEXIFに合わせ、透明度は保持します。画像が読めない場合はモデル読み込み前にエラーにします。
入力画像のパスは出力JSONの `images` に記録します。画像を指定しなければ従来のテキスト画像生成になります。
出力サイズは `--size` で指定する正方形です。

## GPUの簡易確認

```bash
.venv/bin/python check_gpu.py
```

## バージョン

インストール済みのPythonパッケージは `requirements.lock.txt` に記録しています。
ROCm関連パッケージの再取得にはAMD公式配布先 `https://stable.repo.amd.com/rocm/whl-next/` が必要です。
モデルのrevisionは `790c92633540aa0cb11d9abf19eb46d861714758` です。
