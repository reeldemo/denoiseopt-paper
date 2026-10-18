# DenoiseOpt paper — ship status

**Canonical sources:** this repository (`reeldemo/denoiseopt-paper`)  
**Manuscript:** v14 PDF `Unsupervised_Wrap-Discontinuity_Repair_in_Wavetable_Synthesis_via_Hybrid_GA-PPO_Meta-Search_v14.pdf`  
**aiXiv:** https://aixiv.science/abs/aixiv.260719.000003 (`aixiv.260719.000003`, site version 1.7)  
**Status date:** 2026-10-18

## Verdict: manuscript is finished

Peer-review plans A–E and residual weakness phases F1–F5 are complete (see denoise-opt-meta v14 `PLAN_PROGRESS.md` + completion flags).  
Klaut local loop is **stopped** at overall ~6/10 (diminishing returns without a real listening study).  
No open GitHub issues or PRs on this repo.

Primary claims are objective under locked \(R_{\mathrm{blend}}\). That is the honesty ceiling for this campaign.

## Do we need another aiXiv review?

**No — not for scientific content.**

| Check | Result |
|-------|--------|
| Official review status | `official review completed` |
| PDF on aiXiv vs local v14 | **Identical** (same MD5) |
| Local abstract / methods | Current \(R_{\mathrm{blend}}\) framing |

Upload a **new** aiXiv version **only if** you want the *listing page* fixed. That would typically start another review cycle. The PDF body already matches this repo; the HTML listing does not.

### Listing-page gaps (metadata only; not a new science pass)

1. **Abstract on the abs page is stale** — still describes prolonged residual \(R\) vs DualCosine (~0.991 / ~0.825). The PDF abstract is the current \(R_{\mathrm{blend}}\) text from `main.tex`.
2. **Authorship is wrong on the listing** — site lists Cursor / SciSpace / NotebookLM as authors. Correct: **Julian M. Kleber** sole author; those tools belong in Tooling / AI use (already in `subsections/tooling.tex`), not the author line.

When you have aiXiv upload access, re-upload the same PDF (or a rebuild of this tree) with corrected author + abstract fields. Until then, cite the PDF / this GitHub repo.

## Still open — deferred by design (not unfinished drafting)

These are documented limitations / future work, not missing sections:

| Item | Where noted | Why still open |
|------|-------------|----------------|
| Formal MOS / MUSHRA / A/B listening | Limitations; \(N_{\mathrm{listeners}}=0\) | Needs recruitment; required only before any “sounds better” claim |
| Cycle-GAN / BeatDiff / real KIT–PMU depth | `tab:transfer-sota-status`, `DEEP_SOTA_NOT_EXECUTED.json` | OOD / login-walled / metric mismatch — honesty labels already in paper |
| SSM seq models | Results | Explicitly deferred; LSTM remains seq ceiling |
| Multi-seed FitCell-to-plateau (seeds 2–3) | Limitations | Optional compute; seed-1 freeze already reported |
| Klaut score ≥9 | `KLAUT_V14_REVIEW.md` | Blocked without listening study or a different grader |

## What “done” means here

- Build: `.\build.ps1` (or `latexmk`) from this tree.
- Numbers and figures: frozen JSON under `figures/`.
- Search runners: `reeldemo/reelsynth` + `reeldemo/denoise-opt-meta`.
- No further Klaut / weakness-elimination loops planned unless new experiments land.
