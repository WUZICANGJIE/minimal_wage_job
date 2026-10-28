"""基礎案の解説動画をつくる：台本 → 画面（HTML→PNG）＋音声（Kokoro TTS）→ MP4＋SRT。

使い方（video/ で実行）:
    python make_figures.py
    python build_video.py --model kokoro-v1.0.onnx --voices voices-v1.0.bin

中間ファイルは build/（.gitignore 対象）に置く。
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from script_ja import CHAPTERS, SCENES

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
SR = 24000
GAP_SENT, GAP_STEP, GAP_SCENE = 0.3, 0.5, 0.9   # 文・段階・場面の後の無音（秒）
MAX_SUB = 38                                     # 字幕1枚あたりの最大文字数の目安

# ---------------------------------------------------------------- 読みと字幕

MARKUP = re.compile(r"\{([^|{}]+)\|([^{}]+)\}")
DIGITS = "〇一二三四五六七八九"
LETTERS = dict(zip("abcdefghijklmnopqrstuvwxyz", (
    "エー ビー シー ディー イー エフ ジー エイチ アイ ジェー ケー エル エム エヌ オー ピー "
    "キュー アール エス ティー ユー ブイ ダブリュー エックス ワイ ゼット").split()))


def _int_kanji(n):
    if n == 0:
        return "ゼロ"
    out = ""
    for unit, size in (("億", 10**8), ("万", 10**4), ("", 1)):
        q, n = divmod(n, size)
        if q:
            part = ""
            for u, s in (("千", 1000), ("百", 100), ("十", 10), ("", 1)):
                d, q = divmod(q, s)
                if d:
                    part += ("" if d == 1 and u else DIGITS[d]) + u
            out += part + unit
    return out


def _num(m):
    sign, body, pct = m.group(1), m.group(2).replace(",", ""), m.group(3)
    head, _, frac = body.partition(".")
    frac = frac.rstrip("0")
    word = _int_kanji(int(head))
    if frac:
        word += "点" + "".join("ゼロ" if c == "0" else DIGITS[int(c)] for c in frac)
    pre = {"−": "マイナス", "-": "マイナス", "+": "プラス"}.get(sign, "")
    return pre + word + ("パーセント" if pct else "")


def to_reading(text):
    """音声合成用：{表示|読み} を読みに、数値を漢数字に直す。"""
    text = MARKUP.sub(lambda m: m.group(2), text)
    text = re.sub(r"([−+-]?)(\d[\d,]*(?:\.\d+)?)(%?)", _num, text)
    text = re.sub(r"[A-Za-z]+", lambda m: "".join(LETTERS[c.lower()] for c in m.group()), text)
    return text.replace("「", "").replace("」", "")


def to_display(text):
    return MARKUP.sub(lambda m: m.group(1), text)


def sentences(step_text):
    return [s + "。" for s in step_text.split("。") if s.strip()]


def sub_chunks(sentence):
    """長い文を読点で区切り、字幕1枚に収まる塊にする。"""
    disp = to_display(sentence)
    if len(disp) <= MAX_SUB:
        return [disp]
    parts = re.split(r"(?<=、)", disp)
    chunks, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > MAX_SUB:
            chunks.append(cur)
            cur = ""
        cur += p
    chunks.append(cur)
    return chunks

# ---------------------------------------------------------------- 画面


def step_css(max_step=10):
    rules = []
    for s in range(max_step):
        for k in range(max_step):
            if k > s:
                rules.append(f'body[data-step="{s}"] .a{k}{{visibility:hidden}}')
            if k == s:
                rules.append(f'body[data-step="{s}"] .h{k}{{background:var(--hl);'
                             'box-shadow:0 0 0 6px var(--hl);border-radius:6px}')
        rules.append(f'body[data-step="{s}"] [data-only]:not([data-only~="{s}"]){{display:none}}')
    return "\n".join(rules)


CSS = (HERE / "style.css").read_text(encoding="utf-8")


def scene_html(i, sc, katex):
    chap = ""
    if sc["chapter"] is not None:
        tabs = "".join(f'<span class="tab{" on" if j == sc["chapter"] else ""}">{c}</span>'
                       for j, c in enumerate(CHAPTERS))
        chap = f'<header><div class="tabs">{tabs}</div><h1>{sc["title"]}</h1></header>'
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<base href="{HERE.as_uri()}/">
<link rel="stylesheet" href="{katex}/katex.min.css">
<script src="{katex}/katex.min.js"></script>
<script src="{katex}/contrib/auto-render.min.js"></script>
<style>{CSS}
{step_css()}</style></head>
<body data-step="0"><div class="frame">{chap}<main>{sc["body"]}</main></div>
<div id="sub"></div>
<script>
renderMathInElement(document.body, {{delimiters:[{{left:"$$",right:"$$",display:true}},
  {{left:"\\\\(",right:"\\\\)",display:false}}], trust:true, strict:false}});
document.fonts.ready.then(() => {{ window.__ready = true; }});
</script></body></html>"""


def build_plan():
    """場面→段階→文→字幕の塊、の順に並べた計画を作る。"""
    plan = []
    for i, sc in enumerate(SCENES):
        for k, step in enumerate(sc["steps"]):
            sents = sentences(step)
            for j, s in enumerate(sents):
                gap = GAP_SENT
                if j == len(sents) - 1:
                    gap = GAP_SCENE if k == len(sc["steps"]) - 1 else GAP_STEP
                plan.append(dict(scene=i, step=k, text=s, reading=to_reading(s),
                                 chunks=sub_chunks(s), gap=gap))
    return plan

# ---------------------------------------------------------------- 音声


def synthesize(plan, model, voices, voice, speed):
    from kokoro_onnx import Kokoro
    from misaki import ja
    g2p, tts = ja.JAG2P(), Kokoro(model, voices)
    adir = BUILD / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    log = []
    for n, item in enumerate(plan):
        r = g2p(item["reading"])
        ph = r[0] if isinstance(r, tuple) else r
        audio, sr = tts.create(ph, voice=voice, speed=speed, lang="ja", is_phonemes=True)
        assert sr == SR
        # 文頭・文末の無音を軽く詰める
        nz = np.flatnonzero(np.abs(audio) > 0.01)
        audio = audio[max(nz[0] - 600, 0): nz[-1] + 1200] if len(nz) else audio
        item["dur"] = len(audio) / SR
        sf.write(adir / f"{n:04d}.wav", audio, SR)
        log.append(f"{n:04d}\t{item['reading']}\t{ph}")
    (BUILD / "phonemes.tsv").write_text("\n".join(log) + "\n", encoding="utf-8")


def concat_audio(plan):
    parts = []
    for n, item in enumerate(plan):
        a, _ = sf.read(BUILD / "audio" / f"{n:04d}.wav", dtype="float32")
        parts += [a, np.zeros(int(item["gap"] * SR), dtype="float32")]
    lead = np.zeros(int(0.5 * SR), dtype="float32")
    full = np.concatenate([lead] + parts)
    full = full / max(1e-6, np.abs(full).max()) * 0.89
    sf.write(BUILD / "narration.wav", full, SR)
    return 0.5

# ---------------------------------------------------------------- 組み立て


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def frames_and_subs(plan, lead):
    """字幕の塊ごとに1枚の画面。長さは文の音声を文字数で按分する。"""
    frames, subs, t = [], [], lead
    for item in plan:
        total = sum(len(c) for c in item["chunks"])
        for c_i, chunk in enumerate(item["chunks"]):
            d = item["dur"] * len(chunk) / total
            if c_i == len(item["chunks"]) - 1:
                d += item["gap"]
            subs.append((t, t + d - (item["gap"] if c_i == len(item["chunks"]) - 1 else 0),
                         chunk))
            frames.append(dict(scene=item["scene"], step=item["step"], sub=chunk, dur=d))
            t += d
    frames[0]["dur"] += lead
    return frames, subs, t


def render(frames, katex):
    hdir = BUILD / "html"
    hdir.mkdir(parents=True, exist_ok=True)
    pdir = BUILD / "frames"
    pdir.mkdir(exist_ok=True)
    jobs = []
    for i, sc in enumerate(SCENES):
        html = hdir / f"scene_{i:02d}.html"
        html.write_text(scene_html(i, sc, katex), encoding="utf-8")
        shots = [dict(step=f["step"], sub=f["sub"], out=str(pdir / f"{n:04d}.png"))
                 for n, f in enumerate(frames) if f["scene"] == i]
        jobs.append(dict(html=str(html), shots=shots))
    (BUILD / "jobs.json").write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8")
    subprocess.run(["node", str(HERE / "render_frames.mjs"), str(BUILD / "jobs.json")],
                   check=True)


def encode(frames, out):
    lines = []
    for n, f in enumerate(frames):
        lines += [f"file 'frames/{n:04d}.png'", f"duration {f['dur']:.3f}"]
    lines.append(f"file 'frames/{len(frames) - 1:04d}.png'")
    (BUILD / "frames.txt").write_text("\n".join(lines) + "\n")
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(BUILD / "frames.txt"),
        "-i", str(BUILD / "narration.wav"),
        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "slow",
        "-tune", "stillimage", "-crf", "24", "-c:a", "aac", "-b:a", "96k", "-ac", "1",
        "-shortest", "-movflags", "+faststart", str(out)], check=True)


def write_script_md(plan, path):
    lines = ["# 解説動画ナレーション原稿（基礎案）", "",
             "`script_ja.py` から自動生成。字幕（.srt）と同じ文。", ""]
    last = None
    for item in plan:
        if item["scene"] != last:
            sc = SCENES[item["scene"]]
            lines += ["", f"## {item['scene']:02d}　{sc['title'] or 'タイトル'}", ""]
            last = item["scene"]
        lines.append(to_display(item["text"]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="kokoro-v1.0.onnx")
    ap.add_argument("--voices", default="voices-v1.0.bin")
    ap.add_argument("--voice", default="jf_alpha")
    ap.add_argument("--speed", type=float, default=1.1)
    ap.add_argument("--katex", default=str(HERE / "node_modules/katex/dist"))
    ap.add_argument("--out", default=str(HERE / "basic_explainer_ja.mp4"))
    ap.add_argument("--skip-tts", action="store_true", help="build/audio を再利用")
    ap.add_argument("--preview", action="store_true", help="画面だけを描く（音声・動画なし）")
    a = ap.parse_args()

    BUILD.mkdir(exist_ok=True)
    plan = build_plan()
    if a.preview:
        for item in plan:
            item["dur"] = 1.0
        frames, _, _ = frames_and_subs(plan, 0.0)
        render(frames, Path(a.katex).resolve().as_uri())
        return
    if a.skip_tts:
        for n, item in enumerate(plan):
            item["dur"] = sf.info(BUILD / "audio" / f"{n:04d}.wav").duration
    else:
        synthesize(plan, a.model, a.voices, a.voice, a.speed)
    lead = concat_audio(plan)
    frames, subs, total = frames_and_subs(plan, lead)
    render(frames, Path(a.katex).resolve().as_uri())
    encode(frames, a.out)
    srt = "\n".join(f"{n}\n{srt_time(s)} --> {srt_time(e)}\n{txt}\n"
                    for n, (s, e, txt) in enumerate(subs, 1))
    Path(a.out).with_suffix(".srt").write_text(srt, encoding="utf-8")
    write_script_md(plan, HERE / "narration_ja.md")
    print(f"{len(plan)} sentences, {len(frames)} frames, {total / 60:.2f} min -> {a.out}")


if __name__ == "__main__":
    main()
