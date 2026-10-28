# 基礎案の解説動画

`basic_explainer_ja.mp4`（1920×1080、約11分、日本語ナレーション・字幕焼き込み）は、
`slides.md` の基礎案を、本科で経済学を学んだ組員向けに説明し直した動画です。
数式は残し、各項が何を意味するかを図と強調表示で一つずつ読み上げます。

| ファイル | 内容 |
|---|---|
| `basic_explainer_ja.mp4` | 完成動画 |
| `basic_explainer_ja.srt` | 字幕（動画にも焼き込み済み。翻訳や編集の元に使える） |
| `narration_ja.md` | ナレーション全文（`script_ja.py` から自動生成） |
| `script_ja.py` | 台本と画面構成。**内容を直すときはここだけ編集する** |
| `make_figures.py` | 動画用の図（`figs/`）を `../results/*.csv` と授業用の仮定値から描く |
| `build_video.py` | 台本 → 画面（HTML→PNG）＋音声 → MP4・SRT |
| `render_frames.mjs` / `style.css` | 画面の描画（Playwright + KaTeX） |

## 構成（18場面）

1. 問いとデータ：11月なら早期20県（新賃金）と後期14県（旧賃金）を分けられる／$y_{it}$ の意味
2. 企業のモデル：$w=\max\{w^0,m\}$ → 利潤 → 一階条件（図：追加1人の売上と賃金の交点、利潤の山）→ $N^*(w)$ と弾力性 $-1/(1-\beta)$ → 仮定値の計算（1,000円→1,100円で100→82.64人）
3. 求人と仮説：$H^d$、$V^{HW}$、離職率10％→5％で求人は半分でも雇用は同じ、条件付き仮説
4. データで検証：県内変化 $d_i$（東京都の例）→ 差の差 −1.56 → 月次推移・県別散布 → Welch 区間 [−7.93, 4.82]、片側 p=0.31 → 基準期の感度分析
5. まとめ

数値はすべて `../results/estimates.csv`・`county_changes.csv`・`monthly_means.csv` と `slides.md` に一致させています。
弾力性の式と「100÷1.21」の言い換え以外に、スライドにない主張は加えていません。

## 作り直し方

音声はオフラインのニューラル音声合成 Kokoro（声：`jf_alpha`、速度1.1）。数字・記号は `build_video.py` の
`to_reading()` で漢数字・カタカナ読みに変換してから合成します（例：−1.56 → マイナス一点五六、w → ダブリュー）。
台本内の `{表示|読み}` で、字幕と読みを個別に指定できます。

```bash
cd 2026-11-04/01-basic/video
python -m venv .venv && .venv/bin/pip install -r requirements.txt
npm install                       # KaTeX（Playwright と Chromium は別途用意）
# モデル（約350MB、リポジトリには含めない）
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
.venv/bin/python make_figures.py
.venv/bin/python build_video.py --preview   # 画面だけ確認（build/frames/）
.venv/bin/python build_video.py             # 音声合成から MP4・SRT まで（CPUで約9分）
```

日本語フォントは Noto Sans CJK JP（Ubuntu なら `fonts-noto-cjk`）、エンコードに ffmpeg を使います。
`build/phonemes.tsv` に各文の読みと音素が残るので、読み間違いはそこで確認できます。
