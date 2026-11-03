# Klaut audit follow-up (PR #3) — majors addressed without new compute

Reference: klaut-pro `docs/audits/seam-after.md` on `feat/review-aixiv-gap` (score 4.78/10, 13 majors, 0 blockers).

## Fixed in this commit (text / stats only)

| Audit theme | Change |
|-------------|--------|
| 0.9912 in abstract/intro | Abstract: **Provisional** label + explicit “not holdout mean”; intro: separate bullet, no “above gate” superiority framing in key findings |
| n=3 bake-off in abstract/intro | Paired Δ, bootstrap CI, sign-flip p=0.25 inline; “descriptive / selection only” |
| 11/11 vs 50% | Clarified: eleven OAT configs (1 default + 10 ±50% perturbations) completed 500/500 iters—not an 11/11 win rate at 50% |
| Superiority with overlapping CIs | Multifamily, rust bench, meta bake-off, transfer takeaways softened |
| Small-N pilot/diagnostic | HP sensitivity, rust bench, transfer stress labels; Wilson CIs on win proportions |
| “Best / highest” claims | Replaced with “top descriptive”, “first descriptively”, “largest variance”, pointwise stress-test wording |

## Majors likely still open (need compute or scope)

| Major (inferred) | Why still open |
|------------------|----------------|
| Ten-seed holdout / powered paired test | **E1** not run (`EXPERIMENT_PLAN.md`) |
| Multi-search-seed FitCell-to-plateau + holdout replication of 0.9912 | **E2** not run |
| Extra meta-compare search seeds (stable ranking) | **E3** not run |
| GA / PPO / PBT matched-5k ablation | **E4** not run |
| Pareto / campaign export for v2.0 reproducibility | **E5** CPU-only; run on engine logs |
| Formal listening study ($N_{\mathrm{listeners}}=0$) | **E6** human protocol only |
| Hybrid vs N2N on primary holdout (N2N wins all seeds) | Honest limitation; not fixable by prose |
| Factory/AKWF export gaps vs no-bake / N2N | Domain shift; needs new eval or scoped claims |
| Deep transfer / Cycle-GAN / BeatDiff SOTA rows | Already marked incomplete in tables |
| Global HP / Table-2 optimality | OAT probe is pilot only; full 5k re-search not done |
| v2.0 composite-loss / Qseam headline (if audit still cites) | Main line is $R_{\mathrm{blend}}$; legacy metrics in appendix only |
| Engine artifact paths on Julian’s Windows box | Repro outside paper repo |

Re-score after `queue_all.sh` completes and JSON is merged into `figures/multiseed_summary.json` / paper tables.
