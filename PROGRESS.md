# Qwen-Image-2.1 ローカル導入の進捗

更新日: 2026-09-26

## 目的

Qwen-Image-2.1をローカルにインストールし、AMD GPU上でROCmを利用して画像生成できる環境を構築する。

## 公式リンク

- GitHub: https://github.com/QwenLM/Qwen-Image-2.1
- モデル: https://huggingface.co/Qwen/Qwen-Image-2.1
- 実行手順: https://github.com/QwenLM/Qwen-Image-2.1#quick-start
- ハードウェア対応: https://github.com/QwenLM/Qwen-Image-2.1#hardware-support

## 現時点で確認できたこと

- Qwen-Image-2.1は画像生成・画像編集モデル。
- 公式READMEの基本的な実行方法はPython、PyTorch、Diffusersを利用する構成。
- Diffusersの `QwenImage21Pipeline` がモデルを読み込んで画像を生成する。
- このマシンのAMD Radeon 8060S上で、ROCm・PyTorch・Diffusersによる512×512画像生成に成功した。
- 今回の基本構成ではllama.cppを使用しない。
- 公式GitHubリポジトリのcloneは、Diffusersによる基本的な画像生成には必須ではない。READMEやプロンプト書き換え用コードなどの取得に利用できる。
- コードとモデルの重みは別フォルダに配置してよい。

## 想定する構成

| 要素 | 役割 |
| --- | --- |
| 公式GitHubリポジトリのclone（任意） | README、プロンプト書き換え用コードなどの取得 |
| Python仮想環境 | ROCm版PyTorch、Diffusersなどの依存ライブラリを管理 |
| モデル保存フォルダ | Hugging Faceから取得する重み・設定ファイルを保存 |
| 画像生成スクリプト | モデル保存先とプロンプトを指定し、生成画像を保存 |

基本方針は、ROCm版PyTorchとDiffusersの実行環境を用意し、別途保存したモデルを読み込むこと。公式リポジトリをcloneしてビルドするだけで実行環境が完成するわけではない。

## 実施済み

- 公式GitHubおよびモデル配布先を確認した。
- 公式READMEの基本的な実行方法とAMD GPU向けの案内を確認した。
- コード、実行環境、モデルの配置と役割を整理した。

## マシン確認結果（2026-09-26）

- CPU: AMD Ryzen AI MAX+ 395。
- GPU: AMD Radeon 8060S Graphics（Strix Halo / gfx1151、40 CU）。ホスト側の `rocminfo` で認識を確認。
- GPU用メモリ: 48 GiB（51,539,607,552 bytes）。APUのメモリであり、独立したGPUボードのVRAMではない。
- OSから見えるメインメモリ: 約45 GiB、確認時の利用可能量は約40 GiB。Swap 8 GiB。
- OS: Ubuntu 26.04.1 LTS、カーネル `7.0.0-34-generic`。
- ROCm: `amdrocm-*10.0` パッケージ `10.0.0-4` が導入済み。gfx1151向けライブラリあり。HSA Runtime Versionは1.21。
- Python: システムの `python3` は3.14.4。`uv` 導入済み。
- 作業ディスクの空き: 約201 GiB。
- サンドボックス内の `rocminfo` は `/dev/kfd` が見えず失敗したが、承認を得てホスト側で再実行すると正常終了した。
- PyTorchでのGPU演算とQwen-Image-2.1の画像生成を確認済み（結果は下記）。

## 選定した導入構成（2026-09-26）

- Python: 既存の `/usr/bin/python3.14`（3.14.4）を使い、プロジェクト直下の `.venv` に仮想環境を作成する。
- PyTorch: AMD公式配布の `torch[device-gfx1151]==2.13.0+rocm10.0.0`。
- 配布先: `https://stable.repo.amd.com/rocm/whl-next/`。Linux x86_64 / CPython 3.14向けwheelの掲載をcurlで確認済み。
- torchvisionが必要な場合は対応する `torchvision[device-gfx1151]==0.28.0+rocm10.0.0` を使う。音声用のtorchaudioは基本構成には含めない。
- Diffusers: Qwen公式README指定のGitHub版を使う。導入時にコミットを記録して再現可能にする。
- その他: Qwen公式READMEに従い `transformers>=5.17`、`accelerate`、`pillow`。依存解決とimport確認は導入段階で行う。
- モデル保存先（予定）: `models/Qwen-Image-2.1`、画像保存先（予定）: `outputs/`。
- GPU演算確認: モデル取得前にPyTorchからのGPU認識、BF16行列積、SDPAの簡単な演算を確認する。
- `hipconfig --version` は `7.15.26333-0000000` を返した。これは導入済みROCmパッケージのバージョン表記とは別に記録し、PyTorch導入後に `torch.version.hip` も確認する。
- 選定は公式対応情報に基づく。依存関係の解決、インストール、小規模GPU演算とモデルの画像生成を確認済み。

根拠:

- AMD ROCm 10.0リリースノート（Linux PyTorch 2.13.0とPython 3.14の対応）: https://rocm.docs.amd.com/en/latest/about/release-notes.html
- AMD PyTorch導入手順（gfx1151向け指定）: https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html
- 配布wheel一覧: https://stable.repo.amd.com/rocm/whl-next/torch/

## 実行環境の導入・検証結果（2026-09-26）

- `.venv` をPython 3.14.4で作成した。
- 導入済み: PyTorch `2.13.0+rocm10.0.0`、ROCm Pythonパッケージ `10.0.0`、gfx1151向けライブラリ。
- 導入済み: Diffusers `0.41.0.dev0`（コミット `e0abab83b5df05de9e7abd788643c1a7c1e42e28`）、Transformers `5.17.0`、Accelerate `1.15.0`、Pillow `12.3.0`。
- `uv pip check` は51パッケージの整合性を確認し、正常終了。
- 導入バージョン一覧を `requirements.lock.txt` に保存した。再導入時はROCm関連パッケージにAMD公式indexが必要。
- `check_gpu.py` をホスト側で実行して正常終了した。
  - `torch.version.hip`: `7.15.26333`。
  - GPU: AMD Radeon 8060S Graphics / gfx1151、認識メモリ48.0 GiB。
  - BF16行列積（256×256）: CPU FP32結果との比較に合格。
  - BF16 SDPA（1×4×128×64）: CPU FP32結果との比較に合格。
  - `from diffusers import QwenImage21Pipeline`: 成功。
- 再確認コマンド: `.venv/bin/python check_gpu.py`。GPUデバイスにアクセスできるホスト環境で実行する。
- 後続のモデル読み込みでQwen3VLVideoProcessorがtorchvisionを要求したため、`torchvision==0.28.0+rocm10.0.0` とgfx1151用パッケージを追加した。torchaudioは未導入。
- 追加後の `uv pip check` は53パッケージで合格。`requirements.lock.txt` も更新済み。

## モデル取得・画像生成結果（2026-09-26）

- 公式モデルを `models/Qwen-Image-2.1` に取得した（紹介用assetsを除く27ファイル、約33.1 GB / 30.8 GiB）。
- モデルrevision: `790c92633540aa0cb11d9abf19eb46d861714758`。
- `generate.py` を作成。ローカルファイルのみで読み込み、BF16・モデル単位CPUオフロード・VAEタイリングで生成する。
- `HF_HUB_OFFLINE=1` を指定してホスト側で実行し、終了コード0で完了。
- 出力: `outputs/first-image.png`（512×512、RGBA）、設定と計測値: `outputs/first-image.json`。
- プロンプト: 朝の穏やかな緑の森に座る赤いキツネ。生成画像を目視し、内容がプロンプトに対応していることを確認した。
- 設定: 20ステップ、seed 42。
- 初回の生成所要時間: 約60.9秒（プロンプト処理、GPUへの転送、画像変換・保存を含む）。別計測のパイプライン読み込みは約0.53秒。重みの実体読み込み・転送が後段に遅延する可能性があるため、後者だけをモデルロード全体の速度とはみなさない。
- PyTorch計測のGPUメモリピーク: allocated約16.45 GiB、reserved約16.61 GiB。GPU全体・CPUメモリの使用量ではない。
- 再実行方法を `README.md` に記載した。

## 未実施・未確認

- 1024・2048など高解像度での生成時間・メモリ使用量。
- 画像編集、透明背景指定、複数画像入力。

## 次の作業

- `--image`（繰り返し指定可）と `--imagefile`（複数画像パスをまとめて指定）を追加。入力順保持、最大10枚、EXIF回転補正、透明度保持、読み込みエラー処理、出力JSONへのパス記録に対応。モデルをモックした確認で、両オプション併用時の順序・パイプラインへの受け渡し・JSON記録・不明ファイルの事前エラーを検証済み。ユーザーにより複数画像とプロンプトファイルを使った合成画像の生成を確認済み。今回の入力画像・プロンプト・合成結果はGitの管理対象外。

- `generate.py` に `--prompt-file` を追加。UTF-8（BOM付きも可）のファイル全体を読み込み、日本語・複数行に対応。`--prompt` との同時指定、空ファイル、読み込み失敗はエラーにする。

基本的なローカル画像生成の導入と動作確認は完了。必要に応じて解像度やステップ数を変更して利用する。

Python実行環境の導入、モデルのダウンロード、GPUでの画像生成と出力画像の目視確認まで完了。
