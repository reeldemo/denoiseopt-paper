"""Fix broken fig_sota_method_bars + other paper plot label issues (no PowerShell $ expansion)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"

# Multi-family means from locked Table tab:sota-main / sota_matrix (R_blend).
ROWS = [
    ("Ours", 0.931, 0.026),
    ("N2N", 0.925, 0.038),
    ("seq CNN", 0.920, 0.026),
    ("no-bake", 0.893, 0.028),
    ("seam FIR3", 0.868, 0.019),
    ("MLP-on-R", 0.807, 0.018),
    ("CNN/UNet", 0.690, 0.027),
    ("DualCosine", 0.514, 0.032),
    ("soft fade", 0.462, 0.021),
]


def main() -> None:
    labels = [r[0] for r in ROWS][::-1]
    means = np.array([r[1] for r in ROWS][::-1])
    stds = np.array([r[2] for r in ROWS][::-1])
    colors = ["#0072B2"] * len(labels)
    colors[-1] = "#009E73"  # Ours after reverse is last? wait reversed: soft fade first, Ours last
    # After reverse, Ours is at the top of barh (last in list drawn at top in barh? barh plots bottom-first)
    # barh: first element at bottom. We want Ours at top → last in arrays.
    colors = ["#56B4E9"] * (len(labels) - 1) + ["#0072B2"]

    fig, ax = plt.subplots(figsize=(3.35, 2.8), constrained_layout=True)
    y = np.arange(len(labels))
    ax.barh(y, means, xerr=stds, color=colors, height=0.72, error_kw={"ecolor": "#333333", "lw": 0.9, "capsize": 2})
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel(r"$R_{\mathrm{blend}}$ mean $\pm$ std (20 waveforms)", fontsize=8)
    ax.set_title(r"Multi-family $R_{\mathrm{blend}}$ by method", fontsize=9)
    ax.set_xlim(0.35, 1.0)
    ax.grid(True, axis="x", alpha=0.25)
    stem = FIG / "fig_sota_method_bars"
    fig.savefig(stem.with_suffix(".png"), dpi=220)
    fig.savefig(stem.with_suffix(".pdf"))
    plt.close(fig)
    print("wrote", stem.with_suffix(".png"))


if __name__ == "__main__":
    main()
