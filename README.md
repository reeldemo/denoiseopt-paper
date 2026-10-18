# DenoiseOpt paper

Manuscript for *Unsupervised Wrap-Discontinuity Repair in Wavetable Synthesis via Hybrid GA–PPO Meta-Search* (v14).

**Ship status:** finished at the objective-\(R_{\mathrm{blend}}\) honesty ceiling. See [`PAPER_SHIP_STATUS.md`](PAPER_SHIP_STATUS.md).

- **aiXiv:** [aixiv.260719.000003](https://aixiv.science/abs/aixiv.260719.000003) (official review completed; PDF matches this repo; listing abstract/authors need a metadata fix on next upload)
- **Author:** Julian M. Kleber (sole). Cursor / SciSpace / NotebookLM / aixiv assisted tooling — see Tooling section in the PDF, not the author list.

## Build

```powershell
.\build.ps1
```

Requires MiKTeX or TeX Live. Output jobname:

`Unsupervised_Wrap-Discontinuity_Repair_in_Wavetable_Synthesis_via_Hybrid_GA-PPO_Meta-Search_v14.pdf`

## Related repos

| Repo | Role |
|------|------|
| [denoiseopt-paper](https://github.com/reeldemo/denoiseopt-paper) | This manuscript + frozen figure JSON |
| [denoise-opt-meta](https://github.com/reeldemo/denoise-opt-meta) | Meta-search / paper pipeline artifacts |
| [reelsynth](https://github.com/reeldemo/reelsynth) | ReelSynth engine + DenoiseOpt search runners |

## Deferred (not blockers)

Formal listening study; deeper Cycle-GAN / BeatDiff / real KIT–PMU transfer; SSM seq models. Documented in Limitations.
