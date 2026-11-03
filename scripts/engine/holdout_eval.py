"""Score frozen champions on holdout eval seeds (R_blend)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

import torch

from common import DEFAULT_HOLDOUT_SEEDS, bootstrap_reelsynth, save_json, utc_now


def load_n2n(root: Path, device: torch.device):
    bootstrap_reelsynth()
    import overnight_gpu_rl_arch as og  # noqa: E402
    from baselines import n2n_seam  # noqa: E402

    path = root / "brand" / "artifacts" / "n2n_seam_baselines" / "n2n_corrupt_corrupt.pt"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing N2N checkpoint: {path}\n"
            "Train via ./scripts/run_n2n_baseline_retrain.sh or pin reelsynth artifacts."
        )
    blob = torch.load(path, map_location=device, weights_only=False)
    model = n2n_seam.from_state(blob["state_dict"], device)
    model.eval()

    def fn(eng: torch.Tensor) -> torch.Tensor:
        return model(eng)

    return fn, str(path)


def load_hybrid_champ(champ_pt: Path, device: torch.device):
    bootstrap_reelsynth()
    import overnight_gpu_rl_arch as og  # noqa: E402

    blob = torch.load(champ_pt, map_location=device, weights_only=False)
    cfg = og.ArchConfig.from_dict(blob["architecture"])
    cell = og.SeamCell(cfg).to(device)
    cell.load_state_dict(blob["cell_state_dict"])
    cell.eval()

    def fn(eng: torch.Tensor) -> torch.Tensor:
        return og.apply_ops(eng, cell, cfg.ops)

    return fn, cfg, str(champ_pt)


@torch.no_grad()
def score_seed(
    eval_seed: int,
    *,
    device: torch.device,
    batch: int,
    methods: dict[str, Callable[[torch.Tensor], torch.Tensor]],
) -> dict[str, float]:
    import overnight_gpu_rl_arch as og  # noqa: E402

    torch.manual_seed(eval_seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(eval_seed)
    ideal, eng = og.make_batch(batch, og.N, device)
    out: dict[str, float] = {}
    for name, fn in methods.items():
        if name == "no_bake":
            y = eng
        elif name == "dual_cosine":
            y = og.dual_cosine_blend(eng)
        else:
            y = fn(eng)
        r = float(og.residual_score_blend(ideal, eng, y).mean().item())
        out[name] = r
    return out


def eval_holdout(
    *,
    champ_path: Path | None,
    eval_seeds: tuple[int, ...],
    batch: int,
    device: str,
    dry_run: bool,
) -> dict[str, Any]:
    root = bootstrap_reelsynth()
    dev = torch.device(device if device != "cuda" or torch.cuda.is_available() else "cpu")
    if dry_run:
        eval_seeds = (eval_seeds[0],)
        batch = min(batch, 8)

    methods: dict[str, Any] = {}
    n2n_fn, n2n_path = load_n2n(root, dev)
    methods["n2n"] = n2n_fn

    import overnight_gpu_rl_arch as og  # noqa: E402

    methods["dual_cosine"] = og.dual_cosine_blend  # placeholder; scored by name
    methods["no_bake"] = lambda x: x  # placeholder; scored by name

    champ_meta: dict[str, Any] = {}
    if champ_path and champ_path.is_file():
        hybrid_fn, _cfg, cp = load_hybrid_champ(champ_path, dev)
        methods["hybrid"] = hybrid_fn
        champ_meta = {"champ_path": cp}
    elif champ_path:
        champ_meta = {"champ_path": str(champ_path), "missing": True}

    per_seed: dict[str, dict[str, float]] = {}
    t0 = time.time()
    for seed in eval_seeds:
        per_seed[str(seed)] = score_seed(seed, device=dev, batch=batch, methods=methods)

    summary: dict[str, Any] = {}
    for method in methods:
        vals = [per_seed[str(s)][method] for s in eval_seeds]
        summary[method] = {
            "mean": sum(vals) / len(vals),
            "std": (sum((v - sum(vals) / len(vals)) ** 2 for v in vals) / max(len(vals) - 1, 1)) ** 0.5,
            "values": vals,
        }

    return {
        "schema": "denoiseopt.holdout_eval.v1",
        "created_at": utc_now(),
        "dry_run": dry_run,
        "device": str(dev),
        "batch": batch,
        "eval_seeds": list(eval_seeds),
        "champ": champ_meta,
        "n2n_checkpoint": n2n_path,
        "per_seed": per_seed,
        "summary": summary,
        "wall_s": time.time() - t0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--champ", type=Path, default=None)
    ap.add_argument("--holdout-seeds", type=str, default=",".join(map(str, DEFAULT_HOLDOUT_SEEDS)))
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    seeds = tuple(int(s.strip()) for s in args.holdout_seeds.split(",") if s.strip())
    try:
        payload = eval_holdout(
            champ_path=args.champ,
            eval_seeds=seeds,
            batch=args.batch,
            device=args.device,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        print(f"holdout_eval failed: {exc}", file=sys.stderr)
        if args.out.is_file():
            args.out.unlink()
        return 1
    save_json(args.out, payload)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
