"""Build the dynamic-model explainer video (Japanese narration).

Steps: charts from ../results -> narration audio (Kokoro TTS, offline) ->
frames (template.html via Playwright) -> dynamic_explainer.mp4 + .srt + script.md.

Run from anywhere:  python build_video.py
Needs: pip install kokoro-onnx "misaki[ja]" soundfile matplotlib numpy
       npm install (KaTeX), the global playwright package, ffmpeg,
       and the Kokoro v1.0 model files in $KOKORO_DIR (see README.md).
"""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from scenes import SCENES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = HERE / "build"
AUDIO = BUILD / "audio"
FRAMES = BUILD / "frames"
FONT = ROOT / "assets" / "NotoSansJP-Regular.otf"
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", HERE / "models"))
VOICE = "jf_alpha"
SPEED = 1.1
SR = 24000
OUT = HERE / "dynamic_explainer.mp4"

GAP_SENTENCE = 0.35
GAP_STEP = 0.45
GAP_SCENE = 0.9
LEAD_IN = 0.8

MARK = re.compile(r"\{([^|{}]*)\|([^{}]*)\}")
EARLY, LATE, NONE, INK, MUTED = "#2a78d6", "#eb6834", "#a9a7a0", "#111111", "#55534f"


def shown(text):
    return MARK.sub(r"\1", text)


def spoken(text):
    return MARK.sub(r"\2", text)


def num(x):
    return f"{x:.2f}".replace("-", "−")


def sentences(step_text):
    return [s for s in re.split(r"(?<=[。？])", step_text) if s.strip()]


# ---------------------------------------------------------------- charts
def charts():
    import csv

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    font_manager.fontManager.addfont(str(FONT))
    plt.rcParams.update({
        "font.family": font_manager.FontProperties(fname=str(FONT)).get_name(),
        "font.size": 22, "axes.edgecolor": "#888", "axes.linewidth": 1.2,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
    })
    res = ROOT / "results"

    # numeric example: two small panels (v1, v2), bars coloured by scenario
    rows = {r["scenario"]: r for r in csv.DictReader(open(res / "model_assumed_scenarios.csv"))}
    order = [("no_hike", "改定なし", NONE), ("late_anticipated", "晩群", LATE), ("early_anticipated", "早群", EARLY)]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 5.6), dpi=100)
    for ax, (col, label) in zip(axes, [("v1", "今期の募集 $v_1$"), ("v2", "次期の募集 $v_2$")]):
        vals = [float(rows[k][col]) for k, _, _ in order]
        bars = ax.bar(range(3), vals, color=[c for *_, c in order], width=0.62, edgecolor="white", linewidth=2)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.3f}", ha="center", va="bottom", fontsize=19, color=INK)
        ax.set_xticks(range(3), [n for _, n, _ in order])
        ax.set_title(label, fontsize=23, color=INK)
        ax.set_ylim(0, 1.85)
        ax.set_yticks([0, 0.5, 1.0, 1.5])
        ax.grid(axis="y", color="#e6e5e1", linewidth=1)
        ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(BUILD / "numeric.png", transparent=False, facecolor="white")
    plt.close(fig)

    # confidence intervals: main (Jan-Sep base) and sensitivity (Jan-Jul base)
    mc = list(csv.DictReader(open(res / "main_contrasts.csv")))
    by_end = {r["pre_end"]: r for r in mc}
    items = [("主比較（基準 1〜9月）", by_end["9"], INK), ("感度分析（基準 1〜7月）", by_end["7"], MUTED)]
    fig, ax = plt.subplots(figsize=(16, 3.4), dpi=100)
    for i, (lab, r, c) in enumerate(items):
        y = 1 - i
        est, lo, hi = float(r["estimate"]), float(r["ci_low"]), float(r["ci_high"])
        ax.plot([lo, hi], [y, y], color=c, linewidth=4, solid_capstyle="round")
        ax.plot(est, y, "o", color=c, markersize=16, markeredgecolor="white", markeredgewidth=2)
        ax.text(est, y + 0.2, num(est), ha="center", fontsize=21, color=INK)
        ax.text(lo, y - 0.32, num(lo), ha="center", fontsize=18, color=MUTED)
        ax.text(hi, y - 0.32, num(hi), ha="center", fontsize=18, color=MUTED)
    ax.axvline(0, color="#999", linestyle="--", linewidth=1.5)
    ax.text(0.15, 1.45, "0：差がない", fontsize=18, color=MUTED, va="center")
    ax.set_yticks([1, 0], [lab for lab, *_ in items])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlim(-10, 7)
    ax.set_xlabel("早群 − 晩群（基準期からの前年同月比の変化、対数差×100）　点＝推定値、線＝95%区間", fontsize=19)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=21, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(BUILD / "interval.png", facecolor="white")
    plt.close(fig)

    # monthly path of the early-late gap relative to the base period
    pm = list(csv.DictReader(open(res / "monthly_fixed_group_path.csv")))
    months = [r["month"] for r in pm]
    est = np.array([float(r["estimate"]) for r in pm])
    lo = np.array([float(r["ci_low"]) for r in pm])
    hi = np.array([float(r["ci_high"]) for r in pm])
    x = np.arange(len(months))
    nov = months.index("2025-11")
    fig, ax = plt.subplots(figsize=(16, 5.0), dpi=100)
    ax.axvspan(nov + 0.5, len(months) - 0.5, color="#f1f0ec", zorder=0)
    ax.text(nov + 0.7, 9.2, "12月以降：晩群も順次発効（記述のみ）", fontsize=19, color=MUTED, va="top")
    ax.fill_between(x, lo, hi, color=EARLY, alpha=0.13, linewidth=0)
    ax.plot(x, est, color=EARLY, linewidth=2.5, marker="o", markersize=8, markeredgecolor="white", markeredgewidth=1.5)
    ax.axhline(0, color="#999", linewidth=1.2)
    ax.axvline(nov, color=INK, linestyle=":", linewidth=2)
    ax.annotate(f"11月 {num(est[nov])}", (nov, est[nov]), xytext=(nov - 3.2, -9.5), fontsize=20, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK, linewidth=1))
    labels = [f"{int(m[5:])}月" if m[5:] != "01" else f"{m[:4]}\n1月" for m in months]
    ax.set_xticks(x, labels, fontsize=17)
    ax.set_xlim(-0.5, len(months) - 0.5)
    ax.set_ylim(-13, 10)
    ax.set_ylabel("早晩差 − 基準期の早晩差", fontsize=19)
    ax.grid(axis="y", color="#e6e5e1", linewidth=1)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(BUILD / "path.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- audio
_tts = None


def tts(text):
    """Return (samples, cache path) for one spoken sentence."""
    global _tts
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = AUDIO / f"{key}.wav"
    if not path.exists():
        if _tts is None:
            from kokoro_onnx import Kokoro
            from misaki import ja
            _tts = (Kokoro(str(KOKORO_DIR / "kokoro-v1.0.onnx"), str(KOKORO_DIR / "voices-v1.0.bin")), ja.JAG2P())
        model, g2p = _tts
        ph = g2p(text)
        ph = ph[0] if isinstance(ph, tuple) else ph
        samples, sr = model.create(ph, voice=VOICE, speed=SPEED, lang="ja", is_phonemes=True)
        assert sr == SR
        sf.write(path, samples, SR)
    data, _ = sf.read(path, dtype="float32")
    return data


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main(preview=False):
    for d in (BUILD, AUDIO, FRAMES):
        d.mkdir(parents=True, exist_ok=True)
    charts()
    (BUILD / "scenes.js").write_text(
        "window.SCENES = " + json.dumps([{k: s[k] for k in ("tag", "title", "body", "steps")} for s in SCENES],
                                        ensure_ascii=False) + ";\n", encoding="utf-8")

    # timeline: one frame per sentence
    items = []
    for si, sc in enumerate(SCENES):
        for ki, step in enumerate(sc["steps"], start=1):
            sents = sentences(step)
            for ji, sent in enumerate(sents):
                gap = GAP_SENTENCE
                if ji == len(sents) - 1:
                    gap = GAP_SCENE if ki == len(sc["steps"]) else GAP_STEP
                items.append(dict(scene=si, step=ki, sub=shown(sent), say=spoken(sent), gap=gap,
                                  out=str(FRAMES / f"{si:02d}_{ki:02d}_{ji:02d}.png")))

    if preview:
        # layout check only: last sentence of every step, no audio
        keep = [it for n, it in enumerate(items) if n + 1 == len(items) or items[n + 1]["step"] != it["step"]
                or items[n + 1]["scene"] != it["scene"]]
        for it in keep:
            it["progress"] = 0.5
            it["out"] = it["out"].replace("/frames/", "/preview/")
        (BUILD / "preview").mkdir(exist_ok=True)
        (BUILD / "frames.json").write_text(json.dumps(keep, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["node", "render_frames.mjs"], cwd=HERE, check=True)
        return

    clips, t = [np.zeros(int(LEAD_IN * SR), dtype="float32")], LEAD_IN
    for it in items:
        a = tts(it["say"])
        it["start"], it["dur"] = t, len(a) / SR + it["gap"]
        clips += [a, np.zeros(int(round(it["gap"] * SR)), dtype="float32")]
        t += it["dur"]
    total = t
    audio = np.concatenate(clips)
    sf.write(BUILD / "narration.wav", audio, SR)
    for it in items:
        it["progress"] = (it["start"] + it["dur"]) / total

    (BUILD / "frames.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    subprocess.run(["node", "render_frames.mjs"], cwd=HERE, check=True)

    # concat list: each frame held for its sentence (first frame also covers the lead-in)
    lines = []
    for n, it in enumerate(items):
        dur = it["dur"] + (LEAD_IN if n == 0 else 0)
        lines += [f"file '{it['out']}'", f"duration {dur:.3f}"]
    lines.append(f"file '{items[-1]['out']}'")
    (BUILD / "frames.txt").write_text("\n".join(lines) + "\n")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(BUILD / "frames.txt"),
        "-i", str(BUILD / "narration.wav"),
        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-tune", "stillimage", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(OUT),
    ], check=True)

    with open(OUT.with_suffix(".srt"), "w", encoding="utf-8") as f:
        for n, it in enumerate(items, start=1):
            end = it["start"] + it["dur"] - it["gap"]
            f.write(f"{n}\n{srt_time(it['start'])} --> {srt_time(end)}\n{it['sub']}\n\n")

    with open(HERE / "script.md", "w", encoding="utf-8") as f:
        f.write("# ナレーション原稿（動学版の解説動画）\n\n"
                "`build_video.py` が `scenes.py` から生成。動画の字幕と同じ文。\n\n")
        for si, sc in enumerate(SCENES):
            start = next(it["start"] for it in items if it["scene"] == si)
            f.write(f"## {si + 1}. {sc['title'] or 'タイトル'}（{int(start // 60)}:{int(start % 60):02d}〜）\n\n")
            for step in sc["steps"]:
                f.write(shown(step) + "\n\n")
    print(f"{len(items)} sentences, {total / 60:.1f} min -> {OUT}")


if __name__ == "__main__":
    import sys

    main(preview="--preview" in sys.argv)
