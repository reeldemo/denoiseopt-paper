# Experiment plan (aiXiv v2.0 / v2.1 reviews — compute required)

**Approved queue (Julian, single RTX 3060):** `N2N baseline rerun → E1 → E5 → E4 → E2 → E3` via `scripts/queue_all.sh`.

After retraining `n2n_corrupt_corrupt.pt`, run `./scripts/rerun_n2n_baselines.sh` once (or let `queue_all.sh` run it first when `results/n2n_baseline_rerun_complete.json` does not match `results/n2n_retrain_provenance.json` sha256).

## Launchers (paper repo)

| Step | Script | Driver | Primary JSON output |
|------|--------|--------|---------------------|
| E1 | `scripts/run_e1.sh` | `scripts/engine/e1_holdout_10seed.py` | `results/e1_holdout_10seed.json` (+ `figures/`) |
| E5 | `scripts/run_e5.sh` | `scripts/engine/e5_pareto_export.py` | `results/e5_pareto_export.json` |
| E4 | `scripts/run_e4.sh` | `scripts/engine/e4_branch_ablation.py` | `results/e4_branch_ablation_5k.json` |
| E2 | `scripts/run_e2.sh` | `scripts/engine/e2_v14_converge.py` | `results/e2_v14_converge_multiseed.json` |
| E3 | `scripts/run_e3.sh` | `scripts/engine/e3_meta_extra_seeds.py` | `results/e3_meta_extra_seeds.json` |

**Environment (no secrets in repo):**

Reelsynth **main** may no longer include `scripts/baselines/`; pin a snapshot that does (paper-tested: commit **`0a8567b`**) before running holdout or GPU search:

```bash
export REELSYNTH_ROOT=/path/to/reelsynth
git -C "$REELSYNTH_ROOT" fetch origin 0a8567b
git -C "$REELSYNTH_ROOT" checkout 0a8567b   # or a fork tag that restores scripts/baselines/
export PAPER_PYTHON=/path/to/.venv/bin/python   # required; must import torch
cd /path/to/denoiseopt-paper
./scripts/run_e1.sh --dry-run    # each launcher: smoke <2 min (needs N2N ckpt + baselines/)
./scripts/queue_all.sh           # full queue, one GPU job at a time, skips complete JSON
```

Preflight (in `scripts/experiment_env.sh` → `experiment_preflight.sh`) requires **`REELSYNTH_ROOT` explicitly** (no `../reelsynth` guess), existing writable **`results/`** and **`$REELSYNTH_ROOT/brand/artifacts/`**, N2N checkpoint + `scripts/baselines/`, and **`~/bin/research-backup-now`** (mandatory unless `RESEARCH_BACKUP_OPTIONAL=1` for `--dry-run`/CI). Launchers do not create missing output directories.

**Optional — retrain N2N baseline (not started by `queue_all.sh`):**

```bash
./scripts/run_n2n_baseline_retrain.sh              # primary corrupt→corrupt only
./scripts/run_n2n_baseline_retrain.sh --steps 500  # smoke
```

Uses `reelsynth/scripts/train_n2n_seam_baseline.py` (20k steps default). Published log: ~155 s GPU for `n2n_corrupt_corrupt` on RTX 3090; budget **~2.5–3 h** on RTX 3060 for the primary mode alone (~5 h if both modes).

After each launcher step, **`~/bin/research-backup-now <step>` must succeed** (exit 0) or the run aborts. Set `RESEARCH_BACKUP_OPTIONAL=1` only for `--dry-run` or CI (`scripts/tests/`).

`scripts/experiment_env.sh` resolves `ENGINE_PYTHON` from `reelsynth/.venv_gpu` (Linux or Windows layout).
Resume: re-run the same launcher; engine checkpoints (`checkpoint.json`, `history.jsonl`) skip finished arms/seeds.  
Status file: `results/experiment_queue_status.json`.

Long runs write artifacts under **`reelsynth/brand/artifacts/`**; paper repo stores aggregated JSON only.

---

## RTX 3060 wall-clock estimates (vs RTX 3090 plan rows)

Rough scale **×1.35** from published 3090 meta-search walls (`hybrid_lstm` ≈ 8.4 h / 5k iters on 3090). Single GPU, no rental.

| ID | RTX 3060 estimate | Notes |
|----|-------------------|--------|
| E1 | **~3 h** | Rescore frozen champs; 10 eval seeds × 4 methods |
| E5 | **~15 min** | CPU parse of `history.jsonl` |
| E4 | **~135 h** | 4 arms × 3 search seeds @ ~5k evals (GA/PPO/PBT via `overnight_gpu_rl_arch`; full hybrid via `bench_meta_approaches_5k`) + holdout JSON |
| E2 | **~190 h** | 750-iter hybrid converge × 3 search seeds + holdout |
| E3 | **~135 h** | 2 new search seeds × six approaches @ 5k + holdout |
| **Queue total** | **~463 h** | ~19 days continuous on one 3060 |

---

All commands below assume the **reelsynth** repo root with CUDA venv (PyTorch 2.6+cu124 class).  
Holdout evaluation for new search champions: five seeds `20260719`–`20260723` via `scripts/engine/holdout_eval.py` (same locked \(R_{\mathrm{blend}}\), \(\alpha=0.7\)).  
**Do not invent numbers** — copy means into the paper only from emitted JSON.

| ID | Experiment | Review driver | Search seeds (≥3) | Holdout eval | Est. wall / run (3060) | Est. total (3060) |
|----|------------|---------------|-------------------|--------------|------------------------|-------------------|
| E1 | Extend primary holdout to **10 eval seeds** (hybrid short-FitCell, SeamN2N, DualCosine, no-bake) | v2.0 W4; v2.1 Q3 | N/A (eval seeds only) | 10 seeds × 4 methods | ~20 min/rescore batch | **~3 h** |
| E2 | **Multi-search-seed FitCell-to-plateau** (hybrid-only converge) | v2.1 S1; provisional 0.9912 | `1902771841`, `2026072701`, `2026072702` | 5 holdout seeds per champ | ~63 h/search seed | **~190 h** |
| E3 | **Matched 5k + fourth/fifth search seed** for Table meta-approaches | v2.1 S3 | `2026072703`, `2026072704` | per-seed champ → 5 holdout | ~11 h × 6 approaches | **~135 h** |
| E4 | **GA-only / PPO-only / PBT-only** matched 5k arms | v2.1 W4, S4 | `1902771841`, `2026072701`, `2026072702` | 5 holdout seeds per champ | ~11 h/arm/seed | **~135 h** |
| E5 | **Pareto front + champion rule export** (5k campaign logs) | v2.0 W5 | campaign-dependent | N/A | CPU | **~15 min** |
| E6 | **Formal listening study** (MUSHRA, ≥15 listeners) | v2.1 W5; \(N_{\mathrm{listeners}}=0\) | N/A | informal WAVs only today | human time | **out of GPU scope** |

---

## E1 — Ten eval-seed holdout (paired power)

**Goal:** Reach \(p<0.05\) on hybrid vs N2N holdout paired test if effect persists.

```bash
cd denoiseopt-paper
export REELSYNTH_ROOT=../reelsynth
./scripts/run_e1.sh              # full
./scripts/run_e1.sh --dry-run      # smoke
```

**Paper repo follow-up:** rerun `scripts/stats_paired_holdout.py` against the new `multiseed_summary.json`.

---

## E2 — FitCell-to-plateau on three search seeds

**Goal:** Replace single-seed \(R_{\mathrm{blend}}\approx 0.9912\) with mean±std + holdout replication.

```powershell
# Per seed (resume-safe); from REPRO.md
.\scripts\launch_v14_converge_search.ps1 -SearchSeed 2026072701
.\scripts\launch_v14_converge_search.ps1 -SearchSeed 2026072702
# seed 1902771841 already complete
.venv_gpu\Scripts\python.exe scripts\report_v14_converge.py
```

**Holdout gate for each champ:**

```bash
python scripts/eval_champ_holdout_multiseed.py \
  --champ brand/artifacts/meta_approach_compare_v14_converge/<seed>/hybrid_lstm/champ_cell.pt \
  --holdout-seeds 20260719,20260720,20260721,20260722,20260723 \
  --out brand/artifacts/v14_converge_holdout_<seed>.json
```

**Runtime:** ~46.9 h wall × **3 seeds ≈ 141 GPU-hours** (single RTX 3090).

---

## E3 — Extra search seeds for matched 5k bake-off

**Goal:** Stabilize descriptive ranking in Table~\ref{tab:meta-approaches}.

```bash
python scripts/launch_meta_approach_compare.py \
  --iters 5000 \
  --search-seeds 2026072703,2026072704 \
  --out-dir brand/artifacts/meta_approach_compare_v13_rblend
python scripts/bench_meta_approaches_5k.py --aggregate-only \
  --out-dir brand/artifacts/meta_approach_compare_v13_rblend
```

**Runtime:** ~8.4 h × 6 approaches × **2 new seeds ≈ 100 GPU-hours**.

---

## E4 — Hybrid component ablations (matched 5k)

**Goal:** Quantify GA vs PPO vs PBT marginal value under same budget as Table meta-approaches.

Implement or enable branches in `bench_meta_approaches_5k.py`:

- `hybrid_ga_only`, `hybrid_ppo_only`, `hybrid_pbt_only` (disable other branches; same `iters=5000`, same vocab).

```bash
python scripts/bench_meta_approaches_5k.py \
  --approaches hybrid_ga_only,hybrid_ppo_only,hybrid_pbt_only,hybrid_lstm \
  --search-seeds 1902771841,2026072701,2026072702 \
  --iters 5000 \
  --out-dir brand/artifacts/meta_ablate_branches_v1/
```

**Holdout:** rescore each seed’s champion on five eval seeds (as E2).

**Runtime:** ~8.4 h × 4 approaches × 3 seeds ≈ **100 GPU-hours** (order-of-magnitude; branch runs may differ ±20%).

---

## E5 — Pareto front export (5k campaign)

**Goal:** v2.0 reproducibility — selection rule over CR / Δwrap / Rbody if logged.

```bash
python scripts/export_meta_campaign_pareto.py \
  --campaign-dir brand/artifacts/meta_approach_compare_v14_converge/1902771841/ \
  --metrics cr,dwrap,rbody,r_blend \
  --out brand/artifacts/pareto_v14_seed1.json
```

**Runtime:** CPU **<1 h** (requires Windows/engine log paths from original campaign).

---

## E6 — Listening study (\(N_{\mathrm{listeners}}>0\))

**Goal:** Perceptual validation; protocol draft: `figures/LISTENING_PROTOCOL_MAIN.md`.

```bash
python scripts/export_signal_heal_hear_pack.py
python scripts/export_meta_hear_samples.py
# Then run MUSHRA / forced-choice per LISTENING_PROTOCOL_MAIN.md (≥15 listeners)
```

**Runtime:** human study design + analysis; **no GPU** beyond WAV export (~1 h).

---

## Completed without new GPU (this PR)

| Item | Artifact |
|------|----------|
| Holdout + multifamily paired stats | `scripts/stats_paired_holdout.py` → `figures/stats_paired_holdout.json` |
| Matched 5k paired stats (3 search seeds) | `scripts/stats_meta_approach_5k.py` → `figures/stats_meta_approach_5k.json` |
| Notation / symbol table / N2N honesty / listening limitation | `subsections/methods.tex`, `limitations.tex`, `discussion.tex` |

Legacy tracker: `EXPERIMENTS_NEXT.md` (superseded by this file for v2.1 response).
