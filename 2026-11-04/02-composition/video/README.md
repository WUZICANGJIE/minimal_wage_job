# 构成版解说视频（约10分钟，日语旁白）

给组员（本科经济学基础）看的讲解视频：保留模型公式，但逐步展开、配图和例子，帮助在读 `slides.md` 之前先抓住主线。内容与20页正式稿一致，数字直接从 `results/` 的CSV读取，不做新的估计。

## 文件

- `composition_explainer.mp4`：成片（1920×1080，日语合成旁白＋烧录字幕）。
- `composition_explainer.srt`：同内容的字幕文件，可在播放器里另外加载。
- `narration.md`：旁白全文（构建时自动生成），方便对照阅读或改稿。
- `scenes.py`：每一幕的画面（HTML＋KaTeX公式＋SVG图）和旁白句子。改内容只需改这里。
- `build_video.py`：读音转换 → 语音合成 → 截图渲染 → ffmpeg合成。

## 结构

| 章 | 内容 | 对应slides |
|---|---|---|
| はじめに | 问题：规模缩小还是构成变化 | p.1–2 |
| 1 データと比較 | 新规求人的口径；早期20县・后期14县・11月比较 | p.3–4 |
| 2 モデル | 利润最大化、CES与等产量线、一阶条件、相对需求、规模、代替/规模分解、p.11数值例 | p.5–11 |
| 3 検証の方法 | H=qV；前年同月比、相对指标、d与D；−1.56的来历 | p.12–14 |
| 4 結果 | 4个指标的区间图；1–7月基准 | p.16–18 |
| 5 まとめ | 结论与下一步需要的数据 | p.19 |

代替/规模分解里用 σ=2、s_P=0.5 的解析例（代替+1，规模−0.625或−1.67）说明 N 的符号取决于 σ 与 1/(1−β) 的大小，这是由第10页公式直接代入的计算，不是估计。

## 重新构建

旁白用开源的 Kokoro TTS（日语女声 `jf_alpha`），本地离线合成；读音由 misaki/pyopenjtalk 生成。数字、希腊字母和记号由 `build_video.py` 的 `to_speech()` 转成假名读法。

```bash
cd video
pip install -r requirements-video.txt
npm install                      # KaTeX 0.16.22
mkdir -p .models && cd .models   # Kokoro模型（约350MB，不入库）
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ..
python build_video.py --check    # 只打印每句的读音（音素），先检查有没有读错
python build_video.py            # 生成 mp4 / srt / narration.md
```

需要 ffmpeg 和 Chromium（默认 `/opt/pw-browsers/chromium`，可用 `CHROME_PATH` 指定）。模型目录可用 `KOKORO_MODEL_DIR` 指定。

## 注意

- 合成语音偶尔会有不自然的停顿或重音；数字已按“マイナス1点ゴーロク”式读法处理。
- 视频只解释已有结果。所有区间都含0、非兼职不是对照组等边界与正式稿一致。
