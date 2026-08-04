# Sample licenses (Phase F1 wavetable-native realism)

**Date:** 19 July 2026  
**Policy:** license-clean only. No scraped commercial wavetable banks. No LibriSpeech. No MUSDB.

## Primary realism: ReelSynth-exported factory periods

| Item | Detail |
|------|--------|
| Source | True factory bank frames via `cargo run -p reelsynth --release --bin export_reelsynth_wt_cycles` |
| Banks | `saw_morph`, `square_morph`, `sine`, `formant`, `metallic` (ReelSynth MIT factory) |
| Morph positions | frame indices at morph frac $\{0, 0.25, 0.5, 0.75, 1.0\}$ |
| Geometry | source `frame_size=2048` → linear resample → $L{=}256$, peak-normalized |
| License | MIT (ReelSynth) |
| Count | 25 periods |
| Export JSON SHA256 | `f7d03cac45f1651ba0017798eb29d2bff503f9f89cb8cea14554d647f9a788bd` |
| Artifact | `reelsynth/brand/artifacts/real_wt_cycles/reelsynth_export_cycles.json` (local; scored matrix in `paper/v7/figures/real_wt_matrix.json`) |
| Notes | **Not** procedural Python stand-ins. Frame index / morph position recorded in export manifest. |

## Secondary realism: Adventure Kid Waveforms (AKWF) OA pack

| Item | Detail |
|------|--------|
| Source | [AKWF-FREE](https://github.com/KristofferKarlAxelEkstrand/AKWF-FREE) (`AKWF--Akai-MPC/AKWF_0001/AKWF_0001.WAV` … `AKWF_0024.WAV`) |
| Homepage | https://www.adventurekid.se/akrt/waveforms/adventure-kid-waveforms/ |
| License | **CC0-1.0** (Creative Commons Zero v1.0 Universal) |
| Retrieval date | 19 July 2026 |
| Count | 24 single-cycle mono WAVs |
| Crop/resample | fixed-window linear resample to $L{=}256$ (no zero-crossing search); peak-normalize |
| File SHA256 | listed under `meta.oa_file_hashes` in `real_wt_matrix.json` |
| Notes | Third-party OA instrument/WT cycles. Not additive-harmonic procedural stand-ins. |

## Tertiary smoke only (demoted; not claim tables)

| Item | Detail |
|------|--------|
| Source | Procedural factory-like / additive-harmonic generators in `real_wt_wrap_protocol.py` |
| Role | Smoke / regression only (`procedural_standin` key) |
| Notes | Superseded for primary/secondary claims by export + AKWF. |

## Explicitly excluded

- LibriSpeech
- MUSDB / MUSDB18
- Scraped commercial wavetable packs
- Any sample without a recorded OA-compatible license

## Wrap protocol (shared)

1. Close-seam ideal (linear endpoint match).
2. Open-wrap cliff amplitude $\pm\mathcal{U}(0.08,0.43)$ over `SEAM_W=8`.
3. Seam-boosted noise matching `make_batch`.
4. Score prolonged $R$, SNR/SDR, wrap-jump, **edge RMSE** (required secondary seam metric), click energy (optional diagnostic).
