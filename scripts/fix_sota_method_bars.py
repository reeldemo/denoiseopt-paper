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

# Multi-family means from figures/sota_matrix.json (R_blend), refreshed by rerun_n2n_baselines.sh
SOTA = FIG / "sota_matrix.json"


def load_rows() -> list[tuple[str, float, float]]:
    if not SOTA.is_file():
        raise SystemExit(f"Missing {SOTA}; run ./scripts/rerun_n2n_baselines.sh first")
    sota = json.loads(SOTA.read_text(encoding="utf-8"))
    order = [
        ("neural_favorite", "Ours"),
        ("n2n_corrupt_corrupt", "N2N"),
        ("seq_lstm", "seq LSTM"),
        ("seq_cnn1d", "seq CNN"),
        ("no_bake", "no-bake"),
        ("seam_fir3", "seam FIR3"),
        ("mlp_on_R", "MLP-on-R"),
        ("cnn_unet_on_R", "CNN/UNet"),
        ("dual_cosine", "DualCosine"),
    ]
    by = {r["name"]: r for r in sota.get("results_multifamily") or []}
    rows: list[tuple[str, float, float]] = []
    for key, label in order:
        if key not in by:
            continue
        r = by[key]
        rows.append((label, float(r["residual_R_mean"]), float(r.get("residual_R_std") or 0.0)))
    if not rows:
        raise SystemExit(f"No methods found in {SOTA}")
    return rows


def main() -> None:
    rows = load_rows()
    labels = [r[0] for r in rows][::-1]
    means = np.array([r[1] for r in rows][::-1])
    stds = np.array([r[2] for r in rows][::-1])
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
