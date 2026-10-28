# 动学版讲解视频

`dynamic_explainer.mp4`：日文旁白、约12分钟的讲解视频，面向有本科经济学基础的组员。内容跟随 `../slides.md`：两期招聘模型（人数流动 → 收入/募集费用 → 目标函数 → 两期一阶条件 → 比较静态 → 假定值例子）和11月早晚组比较（−1.56，Welch 95% [−7.93, 4.82]，后续路径仅描述）。公式保留，逐步出现并高亮当前讲到的部分，底部有日文字幕。

不是新的分析：图表直接读取 `../results/` 的CSV，数字与slides一致；第13页的假定参数例子同样只是检查数学，不是估计。

## 文件

- `dynamic_explainer.mp4`：成品（1920×1080，H.264/AAC）。
- `dynamic_explainer.srt`：同一字幕的单独文件（可在播放器里另外加载）。
- `script.md`：完整旁白稿（自动生成，按场景附开始时间）。
- `scenes.py`：唯一的手写源稿：16个场景的画面（HTML+KaTeX）与旁白。旁白里 `{显示|读法}` 指定字幕显示与语音读法（公式符号、小数、易读错的汉字）。
- `template.html` / `render_frames.mjs`：用Chromium把每句字幕对应的画面截图。
- `build_video.py`：生成图表 → 合成语音 → 截图 → ffmpeg合成，并写出 `.srt` 与 `script.md`。`--preview` 只截每一步的最后一帧（不合成语音），用于检查版面。

## 重新生成

```bash
cd 2026-11-04/03-dynamic/video
python -m venv .venv && .venv/bin/pip install kokoro-onnx "misaki[ja]" soundfile matplotlib numpy
npm install                       # KaTeX
mkdir -p models && for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  curl -L -o models/$f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f; done
.venv/bin/python build_video.py   # 需要 ffmpeg；playwright 用本目录或全局安装（npm i -g playwright && npx playwright install chromium）
```

语音是离线的 Kokoro v1.0（声音 `jf_alpha`，速度1.1），机器合成，个别读音和语调可能不自然；如需替换为真人录音，可按 `script.md` 逐场景录音。修改旁白只需编辑 `scenes.py` 后重跑，已合成的句子按内容缓存在 `build/audio/`。
