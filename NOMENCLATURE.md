# Nomenclature — baselines and controls

| Manuscript name | Meaning | Legacy JSON / code key |
|-----------------|---------|------------------------|
| **Ideal sibling** $r^{\star}=G(\mathrm{seed},\mathrm{cliff=off})$ | Same generator draw with open-wrap cliff **withheld**. Scoring target only — not a method. | `ideal` |
| **Cracked engine** $x=G(\mathrm{seed},\mathrm{cliff=on})$ | Same seed; cliff applied (FitCell `make_batch` engine path). | `engine` / eng |
| **Seam** (wrap join / loop join) | Local join between end and start of one looped period; click site if endpoints mismatch. Not the whole waveform. | seam / wrap |
| **Repair operator** $\Theta:\mathbb{R}^{L}\times\mathcal{H}\to\mathbb{R}^{L}$ | Searchable local edit at the seam (maps cracked period + config $h$ → baked cycle $y$). Short form after define: **operator**. Legacy code notes: bake cell. | bake cell / ops |
| **Residual operator** | Optional tiny learned network inside a repair operator. | residual cell |
| **No-bake (passthrough)** | Unrepaired cracked engine; $\Theta_{\mathrm{no\text{-}bake}}(x)=x$; then score $R(x,r^{\star})$. | `identity` |
| DualCosine | Raised-cosine end fades on the cracked engine (classical bake). PPO may use $\rho=R-R_{\mathrm{DualCosine}}$ as **advantage centering only**. | `dual_cosine` |
| `seam_fir3` / poly / VA | Other classical (non-AI) repairs on the same $x\to R(\cdot,r^{\star})$ protocol | various |
| Favorite / **Ours** | DenoiseOpt hybrid-search champion bake graph | `favorite` / `hybrid_lstm` |

## Meta-approach comparison labels

Code keys in `meta_approach_compare/` stay stable; **manuscript / table / plot legends** use the short display names below.

| Code key | Manuscript name | What the reader should understand |
|----------|-----------------|-----------------------------------|
| `random` | **Random NAS** | Uniform iid draws over bake graphs + fit HPs (control). |
| `cmaes` | **Cont. CMA-ES** | Diagonal CMA-ES on a continuous encoding of depth/width/blocks/fit HPs. |
| `reinforce` | **Arch REINFORCE** | Vanilla policy gradient on discrete architecture-edit actions (no PPO clip). |
| `aging_evo` | **Aging evolution** | Regularized evolution with oldest-member replacement (Real et al.). |
| `tpe` | **TPE Bayes NAS** | Tree-structured Parzen estimator over discrete bake categoricals. |
| `hybrid_lstm` | **Ours (hybrid GA–PPO)** | Multi-branch GA+PPO+PBT+NAS+combo; LSTM/xLSTM in vocab; co-tunes reward mode + fit/PPO HPs. |

Avoid bare `hybrid_lstm` / “(+LSTM)” in prose — readers cannot tell it is the proposed method.
Keep artifact folder names and JSON `approach` fields as the code keys.

## What is scored against what

```
same seed ──G(cliff=off)──► r*  (ideal sibling; target)
         └──G(cliff=on)───► x  ──Θ(·;h)──► y ──ResidualScore──► R(y, r*)
                              (no-bake: Θ = identity)
```

- **Ideal sibling** = target (cliff off).
- **No-bake** = do nothing to $x$, still score vs $r^{\star}$.
- **Outer objective** = $\max R(y,r^{\star})$; DualCosine centering is PPO advantage only.
- Beating no-bake = closer to $r^{\star}$ than the unrepaired engine.

## Comparison policy

Always rank learned methods on **absolute $R$** vs the full classical non-AI board (no-bake, DualCosine, FIR, poly, fades, VA).
**Reward / objective** = maximize $R$ toward the ideal sibling (best $R{=}1$).
$\Delta R$ vs DualCosine is one classical reporting gap; PPO may center $\rho{=}R-R_{\mathrm{DualCosine}}$, but DualCosine is not the reward.

## Why rename `identity` → no-bake

Reviewers read “identity” as (i) residual-net identity skips, (ii) “what is this method’s identity,” or (iii) a learned identity map.
In this paper it only ever meant **leave the cracked engine unchanged**.
Use **no-bake** / **No-bake (passthrough)** in prose and tables; keep reading `identity` from frozen artifacts.
