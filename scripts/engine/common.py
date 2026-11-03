"""Shared helpers for paper-side experiment drivers (reelsynth on PYTHONPATH)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PAPER_ROOT / "results"
FIGURES_DIR = PAPER_ROOT / "figures"
QUEUE_STATUS = RESULTS_DIR / "experiment_queue_status.json"

DEFAULT_SEARCH_SEEDS = (1_902_771_841, 2_026_072_701, 2_026_072_702)
DEFAULT_HOLDOUT_SEEDS = tuple(range(20_260_719, 20_260_724))
EXTENDED_HOLDOUT_SEEDS = tuple(range(20_260_719, 20_260_729))
E3_EXTRA_SEARCH_SEEDS = (2_026_072_703, 2_026_072_704)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def reelsynth_root() -> Path:
    root = os.environ.get("REELSYNTH_ROOT")
    if not root:
        guess = PAPER_ROOT.parent / "reelsynth"
        if (guess / "scripts").is_dir():
            return guess
        raise SystemExit(
            "REELSYNTH_ROOT not set and ../reelsynth not found. "
            "export REELSYNTH_ROOT=/path/to/reelsynth"
        )
    p = Path(root)
    if not (p / "scripts").is_dir():
        raise SystemExit(f"Invalid REELSYNTH_ROOT (no scripts/): {p}")
    return p


def engine_python() -> str:
    if os.environ.get("ENGINE_PYTHON"):
        return os.environ["ENGINE_PYTHON"]
    root = reelsynth_root()
    for cand in (
        root / ".venv_gpu" / "bin" / "python",
        root / ".venv_gpu" / "Scripts" / "python.exe",
    ):
        if cand.is_file():
            return str(cand)
    return sys.executable


def bootstrap_reelsynth() -> Path:
    root = reelsynth_root()
    scripts = str(root / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return root


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def update_queue_status(experiment: str, **fields: Any) -> None:
    data = load_json(QUEUE_STATUS)
    data.setdefault("experiments", {})
    row = data["experiments"].setdefault(experiment, {})
    row.update(fields)
    row["updated_at"] = utc_now()
    data["updated_at"] = utc_now()
    save_json(QUEUE_STATUS, data)


def is_experiment_complete(experiment: str, result_path: Path) -> bool:
    if not result_path.is_file():
        return False
    payload = load_json(result_path)
    return bool(payload.get("complete"))


def run_subprocess(cmd: list[str], *, cwd: Path | None = None, dry_run: bool = False) -> int:
    print("CMD", " ".join(cmd), flush=True)
    if dry_run:
        return 0
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    return int(proc.returncode)


def og_last_iter(run_dir: Path) -> int:
    hist = run_dir / "history.jsonl"
    if not hist.is_file():
        return 0
    last = 0
    for line in hist.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                last = int(json.loads(line).get("iter") or 0)
            except json.JSONDecodeError:
                continue
    return last


def meta_approach_done(approach_dir: Path, target_iters: int) -> bool:
    ckpt = approach_dir / "checkpoint.json"
    if ckpt.is_file():
        try:
            return int(json.loads(ckpt.read_text(encoding="utf-8")).get("iters_done", 0)) >= target_iters
        except json.JSONDecodeError:
            pass
    summary = approach_dir / "summary.json"
    if summary.is_file():
        try:
            return int(json.loads(summary.read_text(encoding="utf-8")).get("iters_done", 0)) >= target_iters
        except json.JSONDecodeError:
            pass
    return False
