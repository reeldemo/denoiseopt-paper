#!/usr/bin/env python3
"""E2: hybrid FitCell-to-plateau (750 evals) on three search seeds + holdout replication."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from common import (
    DEFAULT_SEARCH_SEEDS,
    FIGURES_DIR,
    RESULTS_DIR,
    engine_python,
    is_experiment_complete,
    load_json,
    meta_approach_done,
    reelsynth_root,
    run_holdout_eval,
    save_json,
    update_queue_status,
    utc_now,
)

CONVERGE_ITERS = 750


def run_converge_seed(seed: int, out_root: Path, *, dry_run: bool) -> dict:
    root = reelsynth_root()
    py = engine_python()
    script = root / "scripts/bench_meta_approaches_5k.py"
    seed_dir = out_root / str(seed)
    approach_dir = seed_dir / "hybrid_lstm"
    iters = 3 if dry_run else CONVERGE_ITERS
    if not meta_approach_done(approach_dir, iters):
        cmd = [
            py,
            str(script),
            "--approaches",
            "hybrid_lstm",
            "--seed",
            str(seed),
            "--iters",
            str(iters),
            "--fit-steps",
            "96" if not dry_run else "24",
            "--out-dir",
            str(seed_dir),
            "--ckpt-every",
            "5" if dry_run else "25",
        ]
        rc = subprocess.run(cmd, cwd=str(root)).returncode
        if rc != 0:
            raise RuntimeError(f"E2 converge search failed seed={seed} rc={rc}")
    summary = load_json(approach_dir / "summary.json")
    champ = approach_dir / "champ_cell.pt"
    return {
        "search_seed": seed,
        "iters": iters,
        "summary": summary,
        "champ_pt": str(champ) if champ.is_file() else None,
        "artifact_dir": str(approach_dir),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out = RESULTS_DIR / "e2_v14_converge_multiseed.json"
    fig_out = FIGURES_DIR / "e2_v14_converge_multiseed.json"
    if not args.force and is_experiment_complete("E2", out):
        print(f"SKIP E2 complete: {out}")
        update_queue_status("E2", status="complete", result=str(out))
        return 0

    update_queue_status("E2", status="running", dry_run=args.dry_run, started_at=utc_now())
    t0 = time.time()
    out_root = reelsynth_root() / "brand/artifacts/meta_approach_compare_v14_converge"
    seeds = DEFAULT_SEARCH_SEEDS
    if args.dry_run:
        seeds = (seeds[0],)

    seed_rows: list[dict] = []
    holdouts: list[dict] = []
    for seed in seeds:
        row = run_converge_seed(seed, out_root, dry_run=args.dry_run)
        seed_rows.append(row)
        champ = row.get("champ_pt")
        if champ and Path(champ).is_file():
            hpath = RESULTS_DIR / f"e2_holdout_search_{seed}.json"
            try:
                hpayload = run_holdout_eval(champ=champ, out=hpath, dry_run=args.dry_run)
            except RuntimeError as exc:
                update_queue_status("E2", status="failed", error=str(exc))
                print(exc, file=sys.stderr)
                return 1
            holdouts.append({"search_seed": seed, "holdout_json": str(hpath), "payload": hpayload})

    payload = {
        "schema": "denoiseopt.e2_v14_converge.v1",
        "experiment": "E2",
        "created_at": utc_now(),
        "dry_run": args.dry_run,
        "complete": not args.dry_run,
        "search_seeds": list(seeds),
        "iters_per_seed": CONVERGE_ITERS,
        "engine_out_root": str(out_root),
        "seeds": seed_rows,
        "holdout_evals": holdouts,
        "wall_s": time.time() - t0,
        "note": (
            "Uses bench_meta_approaches_5k hybrid_lstm with iters=750 and fit-steps=96. "
            "Resume via checkpoint.json in each approach dir. "
            "Seed 1902771841 may already match published 0.9912 in-loop score."
        ),
    }
    save_json(out, payload)
    save_json(fig_out, payload)
    update_queue_status("E2", status="complete" if payload["complete"] else "dry_run_ok", result=str(out))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
