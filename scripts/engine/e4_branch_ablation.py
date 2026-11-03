#!/usr/bin/env python3
"""E4: matched-budget (~5k) hybrid branch ablations (GA / PPO / PBT / full) × search seeds."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from common import (
    DEFAULT_SEARCH_SEEDS,
    FIGURES_DIR,
    PAPER_ROOT,
    RESULTS_DIR,
    engine_python,
    is_experiment_complete,
    load_json,
    meta_approach_done,
    og_last_iter,
    reelsynth_root,
    save_json,
    update_queue_status,
    utc_now,
)

ARMS = (
    ("hybrid_ga_only", "ga"),
    ("hybrid_ppo_only", "ppo"),
    ("hybrid_pbt_only", "pbt"),
    ("hybrid_lstm", "ppo,nas,pbt,ga,combo"),
)


def find_champ_pt(run_dir: Path) -> Path | None:
    for pat in ("**/champ_cell.pt", "**/final_champion_fitted.pt", "**/*champion*fitted.pt"):
        hits = sorted(run_dir.glob(pat))
        if hits:
            return hits[-1]
    return None


def run_overnight_arm(
    *,
    arm: str,
    branches: str,
    seed: int,
    iters: int,
    dry_run: bool,
    device: str,
) -> dict:
    root = reelsynth_root()
    py = engine_python()
    og = root / "scripts/overnight_gpu_rl_arch.py"
    run_id = f"paper-e4-{arm}-{iters}it-{seed}"
    run_dir = root / "brand/artifacts/models" / run_id
    if og_last_iter(run_dir) >= iters:
        print(f"SKIP existing {run_id} iter>={iters}")
    elif dry_run:
        iters = min(iters, 3)
        run_id = f"paper-e4-{arm}-dry-{seed}"
        run_dir = root / "brand/artifacts/models" / run_id
    if og_last_iter(run_dir) < iters:
        cmd = [
            py,
            str(og),
            "--iters",
            str(iters),
            "--seed",
            str(seed),
            "--run-id",
            run_id,
            "--branches",
            branches,
            "--device",
            device,
            "--ckpt-every",
            str(max(25, min(iters, 50))),
            "--plateau-adapt-every",
            "0",
            "--max-hours",
            "200",
            "--algo-tag",
            f"paper-e4:{arm}",
        ]
        rc = subprocess.run(cmd, cwd=str(root)).returncode
        if rc != 0:
            raise RuntimeError(f"overnight_gpu failed rc={rc} arm={arm} seed={seed}")

    hist = run_dir / "history.jsonl"
    last = {}
    if hist.is_file():
        for line in hist.read_text(encoding="utf-8").splitlines():
            if line.strip():
                last = json.loads(line)
    champ_pt = find_champ_pt(run_dir)
    return {
        "arm": arm,
        "branches": branches,
        "seed": seed,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "iters_target": iters,
        "final_iter": int(last.get("iter") or 0),
        "champ_R": float(last.get("champ") or last.get("champ_raw") or 0.0),
        "champ_pt": str(champ_pt) if champ_pt else None,
    }


def run_meta_hybrid(seed: int, iters: int, out_root: Path, dry_run: bool) -> dict:
    root = reelsynth_root()
    py = engine_python()
    script = root / "scripts/bench_meta_approaches_5k.py"
    seed_dir = out_root / str(seed)
    approach_dir = seed_dir / "hybrid_lstm"
    target = min(iters, 3) if dry_run else iters
    if not meta_approach_done(approach_dir, target):
        cmd = [
            py,
            str(script),
            "--approaches",
            "hybrid_lstm",
            "--seed",
            str(seed),
            "--iters",
            str(target),
            "--out-dir",
            str(seed_dir),
            "--ckpt-every",
            "5" if dry_run else "25",
        ]
        rc = subprocess.run(cmd, cwd=str(root)).returncode
        if rc != 0:
            raise RuntimeError(f"bench_meta hybrid_lstm failed seed={seed}")
    summary = approach_dir / "summary.json"
    champ = approach_dir / "champ_cell.pt"
    meta = load_json(summary) if summary.is_file() else {}
    return {
        "arm": "hybrid_lstm",
        "branches": "meta_hybrid_lstm",
        "seed": seed,
        "out_dir": str(approach_dir),
        "iters_target": target,
        "champ_r_blend": meta.get("champ_raw", meta.get("champ_r")),
        "champ_pt": str(champ) if champ.is_file() else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    out = RESULTS_DIR / "e4_branch_ablation_5k.json"
    fig_out = FIGURES_DIR / "e4_branch_ablation_5k.json"
    if not args.force and is_experiment_complete("E4", out):
        print(f"SKIP E4 complete: {out}")
        update_queue_status("E4", status="complete", result=str(out))
        return 0

    update_queue_status("E4", status="running", dry_run=args.dry_run, started_at=utc_now())
    t0 = time.time()
    seeds = DEFAULT_SEARCH_SEEDS
    if args.dry_run:
        seeds = (seeds[0],)

    runs: list[dict] = []
    holdouts: list[dict] = []
    meta_root = reelsynth_root() / "brand/artifacts/paper_e4_meta_hybrid"

    for seed in seeds:
        for arm, branches in ARMS:
            try:
                if arm == "hybrid_lstm":
                    row = run_meta_hybrid(seed, args.iters, meta_root, args.dry_run)
                else:
                    row = run_overnight_arm(
                        arm=arm,
                        branches=branches,
                        seed=seed,
                        iters=args.iters,
                        dry_run=args.dry_run,
                        device=args.device,
                    )
                runs.append(row)
                champ = row.get("champ_pt")
                if champ and Path(champ).is_file():
                    hout = RESULTS_DIR / f"e4_holdout_{arm}_{seed}.json"
                    cmd = [
                        sys.executable,
                        str(PAPER_ROOT / "scripts/engine/holdout_eval.py"),
                        "--champ",
                        champ,
                        "--out",
                        str(hout),
                    ]
                    if args.dry_run:
                        cmd.append("--dry-run")
                    subprocess.run(cmd, cwd=str(PAPER_ROOT), check=False)
                    if hout.is_file():
                        holdouts.append({"arm": arm, "seed": seed, "path": str(hout)})
            except RuntimeError as exc:
                update_queue_status("E4", status="failed", error=str(exc))
                print(exc, file=sys.stderr)
                return 1

    payload = {
        "schema": "denoiseopt.e4_branch_ablation.v1",
        "experiment": "E4",
        "created_at": utc_now(),
        "dry_run": args.dry_run,
        "complete": not args.dry_run,
        "iters_per_arm": args.iters,
        "search_seeds": list(seeds),
        "arms": [{"name": a, "branches": b} for a, b in ARMS],
        "runs": runs,
        "holdout_evals": holdouts,
        "wall_s": time.time() - t0,
        "note": (
            "GA/PPO/PBT arms use overnight_gpu_rl_arch.py with isolated --branches; "
            "hybrid_lstm arm uses bench_meta_approaches_5k.py (matched outer loop). "
            "Resume: re-run launcher; completed runs skipped via history/checkpoint."
        ),
    }
    save_json(out, payload)
    save_json(fig_out, payload)
    update_queue_status("E4", status="complete" if payload["complete"] else "dry_run_ok", result=str(out))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
