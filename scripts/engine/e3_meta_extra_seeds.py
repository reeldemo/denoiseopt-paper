#!/usr/bin/env python3
"""E3: matched 5k outer-loop compare on two additional search seeds (full six approaches)."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from common import (
    E3_EXTRA_SEARCH_SEEDS,
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

APPROACHES = "random,cmaes,reinforce,aging_evo,tpe,hybrid_lstm"
META_ITERS = 5000


def run_seed(seed: int, out_root: Path, *, iters: int, dry_run: bool) -> dict:
    root = reelsynth_root()
    py = engine_python()
    script = root / "scripts/bench_meta_approaches_5k.py"
    seed_dir = out_root / str(seed)
    target = min(iters, 2) if dry_run else iters
    names = [a.strip() for a in APPROACHES.split(",")]
    pending = [
        n
        for n in names
        if not meta_approach_done(seed_dir / n, target)
    ]
    if pending:
        cmd = [
            py,
            str(script),
            "--approaches",
            ",".join(pending),
            "--seed",
            str(seed),
            "--iters",
            str(target),
            "--out-dir",
            str(seed_dir),
            "--ckpt-every",
            "2" if dry_run else "25",
        ]
        rc = subprocess.run(cmd, cwd=str(root)).returncode
        if rc != 0:
            raise RuntimeError(f"E3 meta compare failed seed={seed} rc={rc}")
    summaries = {}
    for n in names:
        summaries[n] = load_json(seed_dir / n / "summary.json")
    return {"search_seed": seed, "out_dir": str(seed_dir), "summaries": summaries}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out = RESULTS_DIR / "e3_meta_extra_seeds.json"
    fig_out = FIGURES_DIR / "e3_meta_extra_seeds.json"
    if not args.force and is_experiment_complete("E3", out):
        print(f"SKIP E3 complete: {out}")
        update_queue_status("E3", status="complete", result=str(out))
        return 0

    update_queue_status("E3", status="running", dry_run=args.dry_run, started_at=utc_now())
    t0 = time.time()
    out_root = reelsynth_root() / "brand/artifacts/meta_approach_compare_v13_rblend"
    seeds = E3_EXTRA_SEARCH_SEEDS

    rows = []
    holdouts = []
    for seed in seeds:
        rows.append(run_seed(seed, out_root, iters=META_ITERS, dry_run=args.dry_run))
        hybrid_dir = out_root / str(seed) / "hybrid_lstm"
        champ = hybrid_dir / "champ_cell.pt"
        if champ.is_file():
            hpath = RESULTS_DIR / f"e3_holdout_hybrid_{seed}.json"
            try:
                run_holdout_eval(champ=champ, out=hpath, dry_run=args.dry_run)
            except RuntimeError as exc:
                update_queue_status("E3", status="failed", error=str(exc))
                print(exc, file=sys.stderr)
                return 1
            holdouts.append({"search_seed": seed, "holdout_json": str(hpath)})

    payload = {
        "schema": "denoiseopt.e3_meta_extra_seeds.v1",
        "experiment": "E3",
        "created_at": utc_now(),
        "dry_run": args.dry_run,
        "complete": not args.dry_run,
        "search_seeds": list(seeds),
        "iters": META_ITERS,
        "approaches": APPROACHES.split(","),
        "engine_out_root": str(out_root),
        "seeds": rows,
        "holdout_evals": holdouts,
        "wall_s": time.time() - t0,
        "note": "Appends seeds 2026072703/04 to existing v13_rblend tree; resume per approach checkpoint.",
    }
    save_json(out, payload)
    save_json(fig_out, payload)
    update_queue_status("E3", status="complete" if payload["complete"] else "dry_run_ok", result=str(out))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
