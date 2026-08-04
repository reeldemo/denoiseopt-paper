# REPRO — DenoiseOpt paper tables (v14)

## Environment

- Repo: `reelsynth` (`https://github.com/reeldemo/reelsynth`)
- Python: `.venv_gpu/Scripts/python.exe` (CUDA preferred; RTX 3090 class)
- Period length: `L=256`
- Primary metric: locked \(R_{\mathrm{blend}}\) (`α=0.7`) via `overnight_gpu_rl_arch.residual_score` / FitCell converge
- Outer loop under test for converge: **hybrid_lstm only** (chosen after D1 matched bake-off)
- Search seeds: `1902771841`, `2026072701`, `2026072702`
- Holdout seeds: `20260719`–`20260723`
- Noise2Noise train seed: `424242`
- Paper companion: `https://github.com/reeldemo/denoise-opt-meta` (this folder)

## A) Matched 5k outer-loop bake-off (Deferred D1 → Table meta-approaches)

```powershell
# From reelsynth root; do NOT use --force-fresh on an existing D1 tree
.\scripts\launch_meta_approach_compare.ps1   # or equivalent bench_meta_approaches_5k.py launch
# Artifacts: brand/artifacts/meta_approach_compare_v13_rblend/
.venv_gpu\Scripts\python.exe scripts\bench_meta_approaches_5k.py --aggregate-only `
  --out-dir brand/artifacts/meta_approach_compare_v13_rblend
```

## B) Hybrid-only FitCell-to-convergence (v14; Table v14-hybrid-converge)

Paper reports hybrid FitCell-to-plateau seed `1902771841` (`R_blend≈0.9912` at 750/750).

```powershell
# Resume-safe launcher (no --force-fresh)
.\scripts\launch_v14_converge_search.ps1
.\scripts\status_v14_converge.ps1
.venv_gpu\Scripts\python.exe scripts\report_v14_converge.py
# Artifacts: brand/artifacts/meta_approach_compare_v14_converge/
# Design note: docs/superpowers/specs/2026-07-31-fitcell-converge-meta-search-design.md
```

Key FitCell HPs (locked in runner): `fit_max_steps`, `fit_patience`, `fit_rel_eps`, `lambda_latency`, batch ≈96, `--proposals-per-iter 2`. CUDA dual-FitCell threads are disabled (`--fit-parallel` off on GPU).

## C) Signal-heal transfer (Table transfer-main)

Metric: **locked \(R_{\mathrm{blend}}\)** only (not PESQ/STOI/MOS). Stress test of wrap geometry; not domain SOTA.

```powershell
.venv_gpu\Scripts\python.exe scripts\download_signal_heal_data.py
.venv_gpu\Scripts\python.exe scripts\bench_signal_heal_transfer.py --iters 250 --merge-existing
.venv_gpu\Scripts\python.exe scripts\export_signal_heal_hear_pack.py
```

| Path | Role |
|------|------|
| `brand/artifacts/signal_heal_transfer/results_table.json` | Main table (`primary_metric=r_blend`) |
| `brand/artifacts/signal_heal_transfer/fig_signal_heal_transfer.{png,pdf}` | Bar figure |
| `brand/artifacts/signal_heal_transfer/<dataset>/hybrid_lstm/summary.json` | Per-domain champ |

## D) Hear pack / vibrato (informal; no listening stats)

```powershell
.venv_gpu\Scripts\python.exe scripts\export_meta_hear_samples.py
.venv_gpu\Scripts\python.exe scripts\bench_vibrato_spectrogram.py
```

No MOS/MUSHRA/A/B study was run (`N_listeners=0`). Released WAVs are for informal inspection only.

## E) Rebuild this PDF

```powershell
cd paper/Unsupervised_Wrap-Discontinuity_Repair_in_Wavetable_Synthesis_via_Hybrid_GA-PPO_Meta-Search_v14
.\build.ps1
```

## Honesty

- Synthetic CNC/PMU rows are proxies when KIT / IEEE DataPort are login-walled.
- Transfer boards are wrap-protocol stress tests, not bearing/ECG diagnosis claims.
- No invented MOS or listening significance tests.
