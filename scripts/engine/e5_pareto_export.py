#!/usr/bin/env python3
"""E5: Pareto front + champion selection export from meta-search history.jsonl."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import (
    FIGURES_DIR,
    RESULTS_DIR,
    is_experiment_complete,
    load_json,
    reelsynth_root,
    save_json,
    update_queue_status,
    utc_now,
)


def read_history(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def pareto_front(points: list[dict], *, x_key: str, y_key: str) -> list[dict]:
    """Maximize both x and y."""
    front: list[dict] = []
    for p in points:
        x, y = float(p[x_key]), float(p[y_key])
        dominated = False
        for q in points:
            qx, qy = float(q[x_key]), float(q[y_key])
            if qx >= x and qy >= y and (qx > x or qy > y):
                dominated = True
                break
        if not dominated:
            front.append(p)
    return sorted(front, key=lambda r: (float(r[x_key]), float(r[y_key])), reverse=True)


def champion_by_j(rows: list[dict]) -> dict | None:
    best = None
    best_j = float("-inf")
    for row in rows:
        j = row.get("j")
        if j is None:
            continue
        jf = float(j)
        if jf > best_j:
            best_j = jf
            best = row
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--campaign-dir",
        type=Path,
        default=None,
        help="Directory containing hybrid_lstm/history.jsonl (default: v14 converge seed1)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Parse at most 200 history lines")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out = RESULTS_DIR / "e5_pareto_export.json"
    fig_out = FIGURES_DIR / "e5_pareto_export.json"
    if not args.force and is_experiment_complete("E5", out):
        print(f"SKIP E5 complete: {out}")
        update_queue_status("E5", status="complete", result=str(out))
        return 0

    root = reelsynth_root()
    campaign = args.campaign_dir or (
        root / "brand/artifacts/meta_approach_compare_v14_converge/1902771841"
    )
    hist_paths = list(campaign.rglob("history.jsonl"))
    if not hist_paths:
        for fallback in (
            root
            / "brand/artifacts/meta_approach_compare_v13_rblend/1902771841/hybrid_lstm/history.jsonl",
            root / "brand/artifacts/meta_approach_compare_v10/hybrid_lstm/history.jsonl",
            root / "brand/artifacts/meta_approach_compare/hybrid_lstm/history.jsonl",
        ):
            if fallback.is_file():
                hist_paths = [fallback]
                break
    if not hist_paths:
        print(f"ERROR: no history.jsonl under {campaign}", file=__import__("sys").stderr)
        update_queue_status("E5", status="failed", error="no history")
        return 2

    update_queue_status("E5", status="running", dry_run=args.dry_run, started_at=utc_now())

    campaigns_out: list[dict] = []
    for hp in hist_paths:
        rows = read_history(hp)
        if args.dry_run:
            rows = rows[:200]
        points = []
        for row in rows:
            rb = row.get("champ_raw", row.get("r_blend", row.get("champ")))
            if rb is None:
                continue
            t_ms = float(row.get("t_ms") or row.get("champ_t_ms") or 0.0)
            points.append(
                {
                    "iter": int(row.get("iter") or 0),
                    "r_blend": float(rb),
                    "j": float(row.get("j") or row.get("champ_j") or rb),
                    "r_seam": row.get("r_seam"),
                    "r_body": row.get("r_body"),
                    "t_ms": t_ms,
                    "beats_n2n": row.get("beats_n2n"),
                }
            )
        if not points:
            continue
        front = pareto_front(points, x_key="r_blend", y_key="j")
        champ = champion_by_j(rows)
        campaigns_out.append(
            {
                "history_path": str(hp),
                "n_rows": len(rows),
                "n_points": len(points),
                "pareto_front_r_blend_vs_j": front[:50],
                "champion_selection_rule": "max J on logged history rows (same as outer-loop selection)",
                "champion_row": champ,
            }
        )

    payload = {
        "schema": "denoiseopt.pareto_export.v1",
        "experiment": "E5",
        "created_at": utc_now(),
        "dry_run": args.dry_run,
        "complete": not args.dry_run,
        "campaign_dir": str(campaign),
        "campaigns": campaigns_out,
    }
    save_json(out, payload)
    save_json(fig_out, payload)
    update_queue_status("E5", status="complete" if payload["complete"] else "dry_run_ok", result=str(out))
    print(f"Wrote {out} ({len(campaigns_out)} histories)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
