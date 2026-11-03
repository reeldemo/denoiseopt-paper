#!/usr/bin/env python3
"""Merge retrained N2N checkpoint scores into paper figure JSON (figures/)."""
from __future__ import annotations

import hashlib
import json
import os
import statistics as st
import sys
from pathlib import Path
from typing import Any

PAPER_ROOT = Path(__file__).resolve().parents[1]
FIGURES = PAPER_ROOT / "figures"
RESULTS = PAPER_ROOT / "results"
PROVENANCE = RESULTS / "n2n_retrain_provenance.json"
HOLDOUT_SEEDS = (20_260_719, 20_260_720, 20_260_721, 20_260_722, 20_260_723)
N2N_METHODS = ("n2n_corrupt_corrupt",)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def reelsynth_root() -> Path:
    root = os.environ.get("REELSYNTH_ROOT")
    if not root:
        raise SystemExit("REELSYNTH_ROOT must be set")
    p = Path(root)
    if not (p / "scripts" / "baselines").is_dir():
        raise SystemExit(f"REELSYNTH_ROOT missing scripts/baselines/: {p}")
    return p


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_provenance() -> str:
    if not PROVENANCE.is_file():
        raise SystemExit(f"Missing provenance: {PROVENANCE}")
    prov = _load(PROVENANCE)
    expected = prov.get("sha256")
    if not expected:
        raise SystemExit(f"Provenance missing sha256: {PROVENANCE}")
    root = reelsynth_root()
    ckpt = root / prov.get("artifact", "brand/artifacts/n2n_seam_baselines/n2n_corrupt_corrupt.pt")
    if not ckpt.is_file():
        raise SystemExit(f"Checkpoint missing: {ckpt}")
    got = sha256_file(ckpt)
    if got != expected:
        raise SystemExit(
            f"N2N checkpoint sha256 mismatch.\n  expected={expected}\n  got={got}\n  path={ckpt}"
        )
    print(f"OK checkpoint sha256={got[:16]}…")
    return got


def bootstrap_reelsynth_scripts() -> Path:
    root = reelsynth_root()
    scripts = str(root / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return root


def copy_json_if_exists(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise SystemExit(f"Expected bench output missing: {src}")
    _save(dst, _load(src))
    print(f"copied {src.name} -> {dst}")


def sync_bench_outputs(root: Path) -> None:
    """Copy reelsynth artifact JSON into paper figures/."""
    pairs = [
        (
            root / "brand/artifacts/n2n_seam_baselines/n2n_baseline.json",
            FIGURES / "n2n_baseline.json",
        ),
        (
            root / "brand/artifacts/v10_n2n_vs_ours/n2n_vs_ours.json",
            FIGURES / "n2n_vs_ours.json",
        ),
        (
            root / "brand/artifacts/cliff_strata.json",
            FIGURES / "cliff_strata.json",
        ),
        (
            root / "brand/artifacts/real_wt_cycles/real_wt_matrix.json",
            FIGURES / "real_wt_matrix.json",
        ),
        (
            root / "brand/artifacts/signal_heal_transfer/latency_table.json",
            FIGURES / "latency_table.json",
        ),
        (
            root / "brand/artifacts/signal_heal_transfer/results_table.json",
            FIGURES / "signal_heal_transfer_results_table.json",
        ),
    ]
    seq_src = root / "brand/artifacts/n2n_seam_baselines/seq_baseline.json"
    if seq_src.is_file():
        pairs.append((seq_src, FIGURES / "seq_baseline.json"))
    for src, dst in pairs:
        copy_json_if_exists(src, dst)
    lat_cmp = root / "brand/artifacts/v13_ours_vs_n2n_latency/latency_compare.json"
    if lat_cmp.is_file():
        copy_json_if_exists(lat_cmp, FIGURES / "latency_compare.json")


def rescore_sota_n2n_rows(*, device: str = "cuda") -> None:
    import torch

    root = bootstrap_reelsynth_scripts()
    import bench_sota_matrix as bsm  # noqa: E402
    import overnight_gpu_rl_arch as og  # noqa: E402
    from baselines import n2n_seam  # noqa: E402

    sota_path = FIGURES / "sota_matrix.json"
    if not sota_path.is_file():
        raise SystemExit(f"Missing {sota_path}")
    payload = _load(sota_path)
    dev = torch.device(device if device != "cuda" or torch.cuda.is_available() else "cpu")

    ckpt_root = root / "brand/artifacts/n2n_seam_baselines"

    def load_fn(name: str):
        ckpt = ckpt_root / f"{name}.pt"
        if name == "n2n_corrupt_corrupt":
            blob = torch.load(ckpt, map_location=dev, weights_only=False)
            model = n2n_seam.from_state(blob["state_dict"], dev)

            def fn(eng: torch.Tensor) -> torch.Tensor:
                return model(eng)

            return fn, int(blob.get("n_params") or 53506)
        if not ckpt.is_file():
            raise SystemExit(f"Missing optional ckpt for sota rescore: {ckpt}")
        blob = torch.load(ckpt, map_location=dev, weights_only=False)
        if name.startswith("n2n"):
            model = n2n_seam.from_state(blob["state_dict"], dev)
        else:
            raise SystemExit(f"Unsupported sota method rescore: {name}")

        def fn2(eng: torch.Tensor) -> torch.Tensor:
            return model(eng)

        return fn2, int(blob.get("n_params") or 53506)

    batch = int(payload.get("score_batch") or 64)

    for block_key in ("results_multifamily",):
        rows = payload.get(block_key)
        if not isinstance(rows, list):
            continue
        dual_by_key = {}
        for r in rows:
            if r.get("name") == "dual_cosine":
                for pw in r.get("per_waveform") or []:
                    dual_by_key[(pw["family"], pw["seed"])] = pw["residual_R"]

        for entry in rows:
            name = entry.get("name")
            if name not in N2N_METHODS:
                continue
            fn, n_params = load_fn(name)
            per_wave = []
            for pw in entry.get("per_waveform") or []:
                fam, seed = pw["family"], pw["seed"]
                ideal, eng = bsm.make_family_batch(fam, batch, og.N, dev, seed=seed)
                m = bsm.score_fn(fn, ideal, eng, n_params=n_params)
                m.update(
                    {
                        "family": fam,
                        "seed": seed,
                        "kind": entry.get("kind", "learned_fixed"),
                        "name": name,
                    }
                )
                per_wave.append(m)
            entry["per_waveform"] = per_wave
            entry["n_waveforms"] = len(per_wave)
            agg = bsm.aggregate_rows(per_wave)
            entry.update(agg)
            deltas = [
                r["residual_R"] - dual_by_key[(r["family"], r["seed"])] for r in per_wave
            ]
            entry["delta_R_vs_dual_cosine_mean"] = float(sum(deltas) / len(deltas))
            entry["delta_R_vs_dual_cosine_std"] = float(
                torch.tensor(deltas, dtype=torch.float64).std(unbiased=False).item()
            )
            print(f"sota rescore {name}: R_mean={entry['residual_R_mean']:.4f}")

    # canonical_holdout block (flat list)
    canon = payload.get("canonical_holdout")
    if isinstance(canon, list):
        dual_r = next(c["residual_R"] for c in canon if c.get("name") == "dual_cosine")
        import bench_canonical_eval_dataset as bced  # noqa: E402

        ideal_c, eng_c = bced.make_frozen_batch(batch, bced.CANONICAL_EVAL_SEED, dev)
        for name in N2N_METHODS:
            fn, n_params = load_fn(name)
            m = bsm.score_fn(fn, ideal_c, eng_c, n_params=n_params, warmup=3, repeats=20)
            for i, c in enumerate(canon):
                if c.get("name") == name:
                    canon[i] = {
                        "name": name,
                        "kind": "learned_fixed",
                        **m,
                        "delta_R_vs_dual_cosine": m["residual_R"] - dual_r,
                    }
                    break

    payload["n2n_retrain_provenance_sha256"] = _load(PROVENANCE).get("sha256")
    _save(sota_path, payload)
    print(f"updated {sota_path}")


def patch_multiseed_summary() -> None:
    """Refresh N2N columns from n2n_vs_ours + holdout_eval + cliff_strata."""
    sys.path.insert(0, str(PAPER_ROOT / "scripts/engine"))
    from common import DEFAULT_HOLDOUT_SEEDS, run_holdout_eval  # noqa: E402

    ms_path = FIGURES / "multiseed_summary.json"
    if not ms_path.is_file():
        raise SystemExit(f"Missing {ms_path}")
    ms = _load(ms_path)

    tmp = RESULTS / "_n2n_holdout_rescore.json"
    holdout_payload = run_holdout_eval(
        champ=None,
        out=tmp,
        holdout_seeds=tuple(DEFAULT_HOLDOUT_SEEDS),
        batch=64,
    )
    per = holdout_payload["per_seed"]
    n2n_vals = [float(per[str(s)]["n2n"]) for s in DEFAULT_HOLDOUT_SEEDS]
    hold = ms.setdefault("holdout", {}).setdefault("holdout", {})
    ps = hold.setdefault("per_seed", {})
    ps["n2n"] = n2n_vals
    hold["n2n_mean"] = st.mean(n2n_vals)
    hold["n2n_std"] = st.stdev(n2n_vals) if len(n2n_vals) > 1 else 0.0

    n2n_vs = _load(FIGURES / "n2n_vs_ours.json")
    mf = n2n_vs.get("multifamily") or {}
    mf_summary = n2n_vs.get("multifamily_summary") or {}
    ours_board = [v["ours"]["R_blend"] for v in mf.values()]
    n2n_board = [v["n2n"]["R_blend"] for v in mf.values()]
    deltas = [o - n for o, n in zip(ours_board, n2n_board)]
    mfold = ms["holdout"].setdefault("multifamily", {})
    mfold["n2n_mean_of_means"] = mf_summary.get("n2n_R_blend_mean", st.mean(n2n_board))
    mfold["n2n_std_of_means"] = st.stdev(n2n_board) if len(n2n_board) > 1 else 0.0
    mfold["board_mean_deltas"] = deltas
    mfold["mean_win_frac"] = sum(1 for d in deltas if d > 0) / max(len(deltas), 1)
    pos = sum(1 for d in deltas if d > 0)
    neg = sum(1 for d in deltas if d < 0)
    mfold["sign_test_on_board_mean_deltas"] = {
        "n": len(deltas),
        "pos": pos,
        "neg": neg,
        "p_two_sided": 1.0 if pos == neg else None,
    }

    cliff_path = FIGURES / "cliff_strata.json"
    if cliff_path.is_file():
        cliff = _load(cliff_path)
        flat = cliff.get("by_stratum", {}).get("all", {})
        n2n_all = flat.get("n2n_corrupt_corrupt", {}).get("R_mean")
        cliff_rows = ms["holdout"].setdefault("cliff", [])
        for row in cliff_rows:
            if n2n_all is not None:
                row["all_n2n"] = n2n_all

    ms["n2n_retrain_provenance_sha256"] = _load(PROVENANCE).get("sha256")
    _save(ms_path, ms)
    print(f"updated {ms_path}")


def write_rerun_complete(sha256: str) -> None:
    out = RESULTS / "n2n_baseline_rerun_complete.json"
    _save(
        out,
        {
            "schema": "denoiseopt.n2n_baseline_rerun_complete.v1",
            "complete": True,
            "n2n_checkpoint_sha256": sha256,
            "provenance": str(PROVENANCE),
        },
    )
    print(f"wrote {out}")


def main() -> int:
    sha = verify_provenance()
    root = reelsynth_root()
    sync_bench_outputs(root)
    device = os.environ.get("N2N_RESCORE_DEVICE", "cuda")
    rescore_sota_n2n_rows(device=device)
    patch_multiseed_summary()
    write_rerun_complete(sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
