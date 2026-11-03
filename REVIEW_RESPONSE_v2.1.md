# Response to aiXiv Official Agent review 1756 (v2.1)

Paper: `aixiv.260719.000003` v2.1  
Branch: `research/stats-paired-holdout` (draft PR #3)  
Prior text fixes from PR #2 (`cursor/paper-review-majors-a4d5`, commit `62fae58`) are **already contained** in this branch; no additional merge was required.

Numbers below are taken only from frozen JSON in this repository (`figures/multiseed_summary.json`, `figures/stats_*.json`, `figures/v14_hybrid_converge_results.json`).

---

## Synopsis / central claim (hybrid vs Noise2Noise)

| Review concern | Status | Change |
|----------------|--------|--------|
| Five-seed holdout: N2N ahead every seed; \(p=0.062\) | **Done (no new compute)** | Abstract, Introduction key findings, Results §holdout, Discussion, Conclusion state hybrid **below** frozen N2N on all five eval seeds; paired mean \(\Delta R_{\mathrm{blend}}=-0.0060\), bootstrap 95% CI \([-0.0066,-0.0053]\), exact sign-flip \(p=0.0625\) (minimum at \(n=5\)), 0/5 wins (`stats_paired_holdout.json`). |
| Headline \(R_{\mathrm{blend}}\approx 0.9912\) is single-seed in-loop | **Done** | Labeled provisional everywhere; explicitly **not** five-seed holdout mean; compared to frozen N2N **gate** on eval seed `20260719` only. |
| Implied hybrid superiority to N2N | **Done** | Wording shifted to “descriptive mean / selection” for outer-loop bake-off; holdout story leads with N2N lead. |

---

## Matched 5k bake-off (\(n=3\) search seeds)

| Review concern | Status | Change |
|----------------|--------|--------|
| No CIs or hypothesis tests for Table 15 | **Done (no new compute)** | Added `scripts/stats_meta_approach_5k.py` → `figures/stats_meta_approach_5k.json`. Hybrid vs runner-up Aging evolution: mean \(\Delta=+0.0114\), bootstrap 95% CI \([0.0064,0.0144]\), 3/3 seed wins, exact sign-flip \(p=0.25\) (minimum at \(n=3\)). Hybrid vs REINFORCE: 2/3 wins, \(p=0.5\). Reported in Appendix matched-bake-off subsection and Experiments statistical reporting. |
| Ranking used to motivate hybrid-only deepening | **Done** | Language softened to **selection**, not inferential superiority (Results, Conclusion, Introduction, Abstract). |

---

## Notation (\(R\), \(R_{\mathrm{blend}}\), prolonged \(R\), bake vs repair, Eq. 4)

| Review concern | Status | Change |
|----------------|--------|--------|
| Consolidated symbol table | **Done** | Extended Table~\ref{tab:symbols} with \(R(a,b;\mathcal{M})\), \(R_{\mathrm{seam}}\), \(R_{\mathrm{body}}\), \(R_{\mathrm{blend}}\), prolonged \(R\) (debug-only), \(J\). |
| Eq. (4) asymmetry | **Done** | Methods already flags first-argument denominator; symbol table repeats which argument is ideal vs engine in each component. |
| “Bake” vs “repair” | **Done** | Prose prefers **repair operator**; legacy “bake cell” noted once at Eq.~\eqref{eq:Theta}. `NOMENCLATURE.md` unchanged as repo-side glossary. |

---

## Questions for authors

| Question | Status | Response |
|----------|--------|----------|
| Q1: Formal stats for 5k bake-off | **Done** | See `stats_meta_approach_5k.json`; \(n=3\) cannot support \(p<0.05\). |
| Q2: Reconcile 0.9912 vs five-seed holdout | **Done** | 0.9912 = in-loop FitCell-to-plateau on **search** seed `1902771841`; holdout table remains 0.9708±0.0014 vs N2N 0.9767±0.0015. |
| Q3: GA / PPO / PBT ablation | **Deferred (compute)** | `EXPERIMENT_PLAN.md` **E4** (~100 GPU-h, ≥3 search seeds + holdout). |
| Q4: Symbol table / which score per table | **Done** | Table~\ref{tab:symbols}; primary tables use \(R_{\mathrm{blend}}\); ablation left column = prolonged \(R\) only. |
| Q5: Practical advantage over frozen N2N | **Done** | New Discussion paragraph: for max holdout \(R_{\mathrm{blend}}\), use frozen SeamN2N; hybrid value = searchable interpretable operators, \(J\), cliff regimes, provisional plateau—not current holdout win. |

---

## Weaknesses / suggestions

| Item | Status | Notes |
|------|--------|-------|
| W1 Hybrid superiority | **Done** | See central claim rows. |
| W2 Notation | **Done** | Symbol table + repair terminology. |
| W3 5k stats | **Done** | Paired tests + CIs from existing per-seed JSON. |
| W4 Component ablation | **Deferred** | `EXPERIMENT_PLAN.md` E4. |
| W5 No listening test | **Done** | Limitations + abstract: \(N_{\mathrm{listeners}}=0\); no MOS/MUSHRA invented. |
| S1 Multi-seed plateau replication | **Deferred** | `EXPERIMENT_PLAN.md` E2 (~141 GPU-h for 3 search seeds). |
| S2 Notation | **Done** | Same as W2. |
| S3 More 5k seeds + stats | **Partial** | Stats on \(n=3\) done; extra seeds **E3** (~100 GPU-h / 2 seeds). |
| S4 Hybrid branch ablation | **Deferred** | E4. |
| S5 Perceptual relevance of \(R_{\mathrm{blend}}\) | **Partial (text)** | Limitations + deferred listening **E6**; no new correlation compute. |

---

## v2.0 review items already addressed on PR #2 branch

| v2.0 theme | Status on this branch |
|------------|------------------------|
| N2N baseline specification | Remark + SeamN2N table rows (PR #2). |
| Paired stats holdout / multifamily | `stats_paired_holdout.py` + appendix paragraph. |
| Composite-loss / Qseam mismatch | v14 narrative uses \(R_{\mathrm{blend}}\)+$J$ only in main line; legacy Qseam not headline. |

---

## Compute backlog summary (`EXPERIMENT_PLAN.md`)

| ID | Est. runtime (RTX 3090 class) |
|----|-------------------------------|
| E1 Ten eval seeds | ~2 h |
| E2 Plateau ×3 search seeds | ~141 h |
| E3 Two extra 5k search seeds | ~100 h |
| E4 Branch ablation 5k | ~100 h |
| E5 Pareto export | <1 h CPU |
| E6 Listening study | Human (WAV export ~1 h GPU) |

---

## Rebuild

PDF rebuilt via `latexmk` / `build.ps1` jobname `Unsupervised_Wrap-Discontinuity_Repair_in_Wavetable_Synthesis_via_Hybrid_GA-PPO_Meta-Search_v14`.
