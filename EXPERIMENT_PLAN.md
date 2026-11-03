# Experiment plan (aiXiv v2.0 / v2.1 reviews — compute required)

All commands assume the **reelsynth** repo root with CUDA venv (RTX 3090 class, PyTorch 2.6+cu124).  
Holdout evaluation for new search champions: five seeds `20260719`–`20260723` via existing multiseed bench scripts (same locked \(R_{\mathrm{blend}}\), \(\alpha=0.7\)).  
**Do not invent numbers** — copy means into the paper only from emitted JSON.

| ID | Experiment | Review driver | Search seeds (≥3) | Holdout eval | Est. wall / run | Est. total |
|----|------------|---------------|-------------------|--------------|-----------------|------------|
| E1 | Extend primary holdout to **10 eval seeds** (hybrid short-FitCell, SeamN2N, DualCosine, no-bake) | v2.0 W4; v2.1 Q3 | N/A (eval seeds only) | 10 seeds × 4 methods | ~15–25 min/GPU (rescore frozen champs) | **~2 h** |
| E2 | **Multi-search-seed FitCell-to-plateau** (hybrid-only converge) | v2.1 S1; provisional 0.9912 | `1902771841`, `2026072701`, `2026072702` (existing) + optional 4th/5th | 5 holdout seeds per champ | ~47 h/search seed (v14 log) | **~141 h** (3 seeds) |
| E3 | **Matched 5k + fourth/fifth search seed** for Table meta-approaches | v2.1 S3 | add e.g. `2026072703`, `2026072704` | per-seed champ → 5 holdout | ~8.4 h × 6 approaches × seed | **~50 h/seed** |
| E4 | **GA-only / PPO-only / PBT-only** matched 5k arms | v2.1 W4, S4 | ≥3: same as D1 list | 5 holdout seeds per champ | ~8 h/arm/seed (hybrid ref) | **~72 h** (3 arms × 3 seeds) |
| E5 | **Pareto front + champion rule export** (5k campaign logs) | v2.0 W5 | campaign-dependent | N/A (post-hoc on logs) | CPU <1 h | **<1 h** |
| E6 | **Formal listening study** (MUSHRA or forced-choice on wrap tiles) | v2.1 W5; \(N_{\mathrm{listeners}}=0\) | N/A | informal WAVs only today | human recruitment | **out of GPU scope** |

---

## E1 — Ten eval-seed holdout (paired power)

**Goal:** Reach \(p<0.05\) on hybrid vs N2N holdout paired test if effect persists.

```bash
# reelsynth root — example pattern (adjust to local bench script names)
python scripts/bench_holdout_multiseed.py \
  --eval-seeds 20260719,20260720,20260721,20260722,20260723,20260724,20260725,20260726,20260727,20260728 \
  --methods hybrid_v10_favorite,n2n_corrupt2corrupt,dual_cosine,no_bake \
  --out brand/artifacts/holdout_multiseed_v14_10seed/
python scripts/aggregate_multiseed_summary.py --root brand/artifacts/holdout_multiseed_v14_10seed/
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
