#!/usr/bin/env python3
"""E1: ten eval-seed holdout rescore (hybrid, N2N, DualCosine, no-bake)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import (
    EXTENDED_HOLDOUT_SEEDS,
    FIGURES_DIR,
    PAPER_ROOT,
    RESULTS_DIR,
    is_experiment_complete,
    load_json,
    reelsynth_root,
    save_json,
    update_queue_status,
    utc_now,
)


def default_hybrid_champ() -> Path:
    root = reelsynth_root()
    rel = (
        "brand/artifacts/meta_approach_compare_v10/hybrid_lstm/champ_cell.pt"
    )
    return root / rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Smoke: 1 seed, small batch, <2 min")
    ap.add_argument("--champ", type=Path, default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out = RESULTS_DIR / "e1_holdout_10seed.json"
    fig_out = FIGURES_DIR / "e1_holdout_10seed.json"
    if not args.force and is_experiment_complete("E1", out):
        print(f"SKIP E1 complete: {out}")
        update_queue_status("E1", status="complete", result=str(out))
        return 0

    champ = args.champ or default_hybrid_champ()
    seeds = EXTENDED_HOLDOUT_SEEDS
    if args.dry_run:
        seeds = (seeds[0],)

    update_queue_status("E1", status="running", dry_run=args.dry_run, started_at=utc_now())

    holdout_script = PAPER_ROOT / "scripts/engine/holdout_eval.py"
    cmd = [
        sys.executable,
        str(holdout_script),
        "--champ",
        str(champ),
        "--holdout-seeds",
        ",".join(map(str, seeds)),
        "--out",
        str(out),
        "--batch",
        "8" if args.dry_run else "64",
    ]
    if args.dry_run:
        cmd.append("--dry-run")
    rc = subprocess.run(cmd, cwd=str(PAPER_ROOT)).returncode
    if rc != 0:
        update_queue_status("E1", status="failed", exit_code=rc)
        return rc

    payload = load_json(out)
    payload["experiment"] = "E1"
    payload["complete"] = not args.dry_run
    payload["note"] = (
        "Ten eval seeds for paired holdout power (v2.0/v2.1). "
        "After full run, merge into multiseed_summary and rerun stats_paired_holdout.py."
    )
    save_json(out, payload)
    save_json(fig_out, payload)

    if not args.dry_run:
        stats = subprocess.run(
            [sys.executable, str(PAPER_ROOT / "scripts/stats_paired_holdout.py")],
            cwd=str(PAPER_ROOT),
        )
        if stats.returncode != 0:
            print("WARN: stats_paired_holdout.py failed (expected until multiseed_summary updated)")

    update_queue_status("E1", status="complete" if payload["complete"] else "dry_run_ok", result=str(out))
    print(f"Wrote {out} and {fig_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
