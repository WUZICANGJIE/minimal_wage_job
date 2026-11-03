"""構成版の解説動画をビルドする。

  python build_video.py --check   # ナレーションの読み（音素）を表示して確認するだけ
  python build_video.py           # 音声合成 → 画面描画 → mp4/srt/narration.md を出力

依存：requirements-video.txt、npm install（KaTeX）、ffmpeg、Chromium、
Kokoroのモデル2ファイル（README参照、既定では video/.models/）。
"""
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from scenes import SCENES, CONTRASTS  # noqa: E402

OUT_MP4 = HERE / "composition_explainer.mp4"
OUT_SRT = HERE / "composition_explainer.srt"
OUT_MD = HERE / "narration.md"
CACHE = HERE / ".cache"
MODELS = Path(os.environ.get("KOKORO_MODEL_DIR", HERE / ".models"))
CHROME = os.environ.get("CHROME_PATH", "/opt/pw-browsers/chromium")
VOICE, SPEED, SR = "jf_alpha", 1.0, 24000
GAP_LINE, GAP_SCENE, LEAD = 0.35, 0.9, 0.6
W, H = 1920, 1080

# ---------------------------------------------------------------- 読み

LETTERS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                   "エー ビー シー ディー イー エフ ジー エイチ アイ ジェー ケー エル エム エヌ オー ピー キュー アール エス ティー ユー ブイ ダブリュー エックス ワイ ゼット".split()))
WORDS = {"CES": "シーイーエス", "methods": "メソッズ", "sources": "ソーシズ",
         "σ": "シグマ", "β": "ベータ", "ρ": "ロー", "Π": "パイ"}
KANA_DIGITS = "ゼロ イチ ニー サン ヨン ゴー ロク ナナ ハチ キュー".split()


def _decimal(m):
    sign = {"−": "マイナス", "-": "マイナス", "+": "プラス"}.get(m.group(1) or "", "")
    ip, fp = m.group(2), m.group(3)
    ip = "れい" if ip == "0" else ip
    return f"{sign}{ip}点{''.join(KANA_DIGITS[int(d)] for d in fp)}"


def to_speech(text):
    """字幕の文をTTS用の読みに直す（数字・記号・ラテン文字）。"""
    s = text
    for k, v in WORDS.items():
        s = s.replace(k, v)
    s = re.sub(r"([A-Za-z])_([A-Za-z])", lambda m: LETTERS[m.group(1).upper()] + LETTERS[m.group(2).upper()], s)
    s = re.sub(r"([−+-]?)(\d+)\.(\d+)", _decimal, s)
    s = re.sub(r"([−+])(\d+)", lambda m: ("マイナス" if m.group(1) == "−" else "プラス") + m.group(2), s)
    s = s.replace("%", "パーセント")
    s = re.sub(r"(?<![A-Za-z])([A-Za-z])(?![A-Za-z])", lambda m: LETTERS[m.group(1).upper()], s)
    if re.search(r"[A-Za-z_]", s):
        raise ValueError(f"読みにラテン文字が残っている: {s}")
    return s


def sub_html(text):
    t = html.escape(text)
    return re.sub(r"([A-Za-zσβ])_([A-Za-z])", r"\1<sub>\2</sub>", t)


def sub_plain(text):
    return re.sub(r"([A-Za-zσβ])_([A-Za-z])", r"\1\2", text)


# ---------------------------------------------------------------- 構造

def timeline():
    """(scene_index, step_index, line) の並び。"""
    items = []
    for si, sc in enumerate(SCENES):
        for ki, st in enumerate(sc["steps"]):
            for line in st["lines"]:
                items.append((si, ki, line))
    return items


def check_numbers():
    """画面・ナレーションの丸め値が results/contrasts.csv と一致することを確認。"""
    text = json.dumps(SCENES, ensure_ascii=False)
    need = {"part": "−1.56", "total": "−0.15", "relative": "−2.23", "nonpart": "+0.67"}
    for m, v in need.items():
        est = float(CONTRASTS[(m, "2025-09")]["estimate"])
        assert f"{abs(est):.2f}" == v[1:], (m, est, v)
        assert v in text, (m, v)
    assert "0.31" in text and "−7.93" in text and "4.82" in text


# ---------------------------------------------------------------- 音声

def tts_all(items):
    from kokoro_onnx import Kokoro
    from misaki import ja
    g2p = ja.JAG2P()
    kok = Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))
    (CACHE / "tts").mkdir(parents=True, exist_ok=True)
    out = []
    for _, _, line in items:
        r = g2p(to_speech(line))
        ph = r[0] if isinstance(r, tuple) else r
        key = hashlib.sha1(f"{VOICE}|{SPEED}|{ph}".encode()).hexdigest()[:16]
        path = CACHE / "tts" / f"{key}.wav"
        if not path.exists():
            audio, sr = kok.create(ph, voice=VOICE, speed=SPEED, lang="ja", is_phonemes=True)
            assert sr == SR
            sf.write(path, audio, sr)
        out.append(path)
    return out


# ---------------------------------------------------------------- 画面

CSS = r"""
@font-face { font-family: "NotoJP"; src: url("../assets/NotoSansJP-Regular.otf"); }
* { box-sizing: border-box; }
html, body { margin: 0; width: 1920px; height: 1080px; background: #fff; color: #111;
  font-family: "NotoJP", sans-serif; overflow: hidden; }
#bar { position: absolute; top: 0; left: 0; height: 8px; background: #1d4ed8; }
#chapter { position: absolute; top: 34px; left: 96px; font-size: 26px; color: #1d4ed8; letter-spacing: .05em; }
#title { position: absolute; top: 74px; left: 96px; right: 96px; font-size: 54px; font-weight: 700; line-height: 1.25; }
#body { position: absolute; top: 210px; left: 96px; right: 96px; bottom: 210px; font-size: 36px; line-height: 1.5;
  display: flex; flex-direction: column; justify-content: center; gap: 22px; }
#sub { position: absolute; left: 50%; transform: translateX(-50%); bottom: 34px; width: 1720px; text-align: center; }
#sub span { display: inline-block; text-wrap: balance; word-break: auto-phrase; background: rgba(15,15,20,.86); color: #fff; font-size: 37px; line-height: 1.45;
  padding: 12px 30px; border-radius: 10px; }
#sub sub, .exp sub { font-size: .7em; }
[data-step].off { visibility: hidden; }
[data-from].off2, [data-only].off2 { display: none; }
.hlon { background: #fef3a0; border-radius: 6px; box-shadow: 0 0 0 8px #fef3a0; }
.note.hlon { background: #fef9c3; box-shadow: none; border-left-color: #ca8a04; }
.eq.hlon { box-shadow: none; background: none; } .eq.hlon .katex-display { background: #fef3a0; border-radius: 10px; display: inline-block; padding: 4px 24px; }
.katex .hlon { box-shadow: 0 0 0 4px #fef08a; }
.katex .blue { color: #1d4ed8; } .katex .orange { color: #c2410c; }
.eq { font-size: 46px; text-align: center; } .eq.sm { font-size: 40px; }
.eq .katex-display { margin: 8px 0; }
.exp { font-size: 32px; color: #333; text-align: center; }
.note { font-size: 34px; background: #f3f4f6; border-left: 10px solid #1d4ed8; padding: 18px 28px; }
.pts { margin: 0; padding-left: 1.2em; } .pts li { margin: 18px 0; } .pts.sm { font-size: 32px; }
.tbl { border-collapse: collapse; margin: 0 auto; font-size: 36px; }
.tbl th, .tbl td { padding: 14px 34px; border-bottom: 2px solid #999; text-align: left; }
.tbl th { border-top: 3px solid #111; border-bottom: 2px solid #111; }
.tbl.num td + td, .tbl.num th + th { text-align: right; }
.hlcell { background: #fef08a; } .hlrow td { background: #eef2ff; }
.two { display: flex; gap: 60px; justify-content: center; }
.card { width: 680px; padding: 34px; border-radius: 14px; font-size: 38px; text-align: center; border: 4px solid; }
.card-h { font-size: 52px; font-weight: 700; margin-bottom: 10px; }
.card.blue { border-color: #1d4ed8; color: #1d3a8a; } .card.orange { border-color: #c2410c; color: #8a2e0b; }
.split { display: flex; gap: 40px; align-items: center; } .split .left { flex: 1; } .split .right { width: 640px; } .split .right.wide { width: 780px; } .split .left .note { font-size: 30px; }
.center { display: flex; justify-content: center; }
.tlrow { display: flex; gap: 30px; justify-content: center; }
.tl { width: 520px; border: 4px solid #999; border-radius: 14px; padding: 26px; text-align: center; }
.tl.e { border-color: #1d4ed8; } .tl.l { border-color: #c2410c; } .tl.x { border-style: dashed; color: #888; }
.tl-when { font-size: 30px; color: #555; } .tl-name { font-size: 46px; font-weight: 700; } .tl-n { font-size: 40px; }
.tl-state { font-size: 28px; margin-top: 8px; }
body.title #title, body.title #chapter { display: none; }
body.title #body { top: 120px; text-align: center; }
.bigtitle { font-size: 76px; font-weight: 700; } .subtitle-l { font-size: 44px; color: #333; } .meta { font-size: 32px; color: #666; }
"""

JS = r"""
function show(k, sub, progress) {
  document.querySelectorAll('[data-step]').forEach(e => e.classList.toggle('off', +e.dataset.step > k));
  document.querySelectorAll('[data-from]').forEach(e => e.classList.toggle('off2', +e.dataset.from > k));
  document.querySelectorAll('[data-only]').forEach(e => e.classList.toggle('off2', +e.dataset.only != k));
  document.querySelectorAll('[data-hl]').forEach(e => e.classList.toggle('hlon', +e.dataset.hl == k));
  for (let n = 0; n < 6; n++) document.querySelectorAll('.hl' + n).forEach(e => e.classList.toggle('hlon', n == k));
  document.getElementById('sub').innerHTML = '<span>' + sub + '</span>';
  document.getElementById('bar').style.width = (progress * 1920) + 'px';
}
"""


def scene_doc(sc):
    body = "\n".join(st["html"] for st in sc["steps"])
    katex = "node_modules/katex/dist"
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<link rel="stylesheet" href="{katex}/katex.min.css">
<script src="{katex}/katex.min.js"></script>
<script src="{katex}/contrib/auto-render.min.js"></script>
<style>{CSS}</style><script>{JS}</script></head>
<body class="{sc.get('cls', '')}"><script>window.__katexErrors = [];</script><div id="bar"></div><div id="chapter">{sc['chapter']}</div>
<div id="title">{sc['title'] or ''}</div><div id="body">{body}</div><div id="sub"></div>
<script>renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}},
 {{left: '$', right: '$', display: false}}], trust: true, strict: false, throwOnError: true,
 errorCallback: (m, e) => window.__katexErrors.push(m + ' ' + e)}});</script>
</body></html>"""


def render_frames(items):
    from playwright.sync_api import sync_playwright
    fdir = CACHE / "frames"
    fdir.mkdir(parents=True, exist_ok=True)
    paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        page = browser.new_page(viewport={"width": W, "height": H})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        current = None
        for n, (si, ki, line) in enumerate(items):
            if si != current:
                doc = HERE / f".scene_{si:02d}.html"
                doc.write_text(scene_doc(SCENES[si]), encoding="utf-8")
                page.goto(doc.as_uri())
                page.evaluate("document.fonts.ready")
                current = si
                kerr = page.evaluate("window.__katexErrors")
                if kerr:
                    raise RuntimeError(f"KaTeX 場面{si}: {kerr}")
                page.evaluate("show(0, '', 0)")
                overflow = page.evaluate("(() => { const b = document.getElementById('body');"
                                         " return b.scrollHeight - b.clientHeight; })()")
                if overflow > 2:
                    print(f"  警告: 場面{si}の本文が{overflow}px はみ出している")
            page.evaluate("([k, s, p]) => show(k, s, p)", [ki, sub_html(line), (si + 1) / len(SCENES)])
            path = fdir / f"f{n:03d}.png"
            page.screenshot(path=str(path))
            paths.append(path)
        browser.close()
        if errors:
            raise RuntimeError(errors)
    for f in HERE.glob(".scene_*.html"):
        f.unlink()
    return paths


# ---------------------------------------------------------------- 結合

def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def assemble(items, wavs, frames):
    chunks = [np.zeros(int(LEAD * SR), dtype=np.float32)]
    t = LEAD
    durations, srt, md = [], [], ["# 解説動画ナレーション（自動生成）", ""]
    last_scene = None
    for n, ((si, ki, line), wav) in enumerate(zip(items, wavs)):
        if si != last_scene:
            sc = SCENES[si]
            md += ["", f"## {sc['chapter']}｜{sc['title'] or '導入'}", ""]
            last_scene = si
        a, sr = sf.read(wav, dtype="float32")
        end_of_scene = n + 1 == len(items) or items[n + 1][0] != si
        gap = GAP_SCENE if end_of_scene else GAP_LINE
        srt.append(f"{n + 1}\n{srt_time(t)} --> {srt_time(t + len(a) / SR)}\n{sub_plain(line)}\n")
        md.append(f"{sub_plain(line)}")
        seg = len(a) / SR + gap
        durations.append(seg + (LEAD if n == 0 else 0))
        chunks += [a, np.zeros(int(round(gap * SR)), dtype=np.float32)]
        t += seg
    audio = np.concatenate(chunks)
    wav_all = CACHE / "narration.wav"
    sf.write(wav_all, audio, SR)
    lst = CACHE / "frames.txt"
    with open(lst, "w") as f:
        for p, d in zip(frames, durations):
            f.write(f"file '{p}'\nduration {d:.4f}\n")
        f.write(f"file '{frames[-1]}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-i", str(wav_all), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "slow",
                    "-tune", "stillimage", "-crf", "24", "-c:a", "aac", "-b:a", "96k", "-ac", "1",
                    "-shortest", "-movflags", "+faststart", str(OUT_MP4)], check=True)
    OUT_SRT.write_text("\n".join(srt), encoding="utf-8")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    return len(audio) / SR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    check_numbers()
    items = timeline()
    if args.check:
        from misaki import ja
        g2p = ja.JAG2P()
        for si, ki, line in items:
            r = g2p(to_speech(line))
            print(f"[{si}.{ki}] {to_speech(line)}\n      {r[0] if isinstance(r, tuple) else r}")
        return
    wavs = tts_all(items)
    print(f"音声 {len(wavs)} 文")
    frames = render_frames(items)
    print(f"画面 {len(frames)} 枚")
    total = assemble(items, wavs, frames)
    print(f"完成 {OUT_MP4.name}: {total / 60:.1f} 分")


if __name__ == "__main__":
    main()
