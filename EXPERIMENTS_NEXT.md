# Experiments required by the aiXiv v2.0 review (and claims in v2.1)

| ID | Experiment | Why (review item) | Compute | Status |
|---|---|---|---|---|
| S1 | Paired stats on existing 5-seed holdout + 20 boards | W4 stats | CPU, seconds | DONE (`scripts/stats_paired_holdout.py`) |
| S2 | Extend holdout to 10 seeds (hybrid, N2N, DualCosine, no-bake) | W4: n=5 cannot reach p<0.05 | engine RTX 3060, ~2–3 h | needs reelsynth artifacts on engine (paths are Julian's Windows box) |
| S3 | Pareto front + champion-selection rule export over the 5k campaign | W5 | CPU, <1 h, needs campaign logs | logs on Windows box |
| S4 | Multi-search-seed replication of v14 hybrid converge (3 search seeds) | provisional N2N-gate claim | ~8 h/seed on 3090-class -> ~24 h; GPU rental suggested (Nov) | Julian decision |
| S5 | Listening study (MUSHRA, ≥15 listeners) | Nlisteners=0 ceiling | human time | Julian decision |
