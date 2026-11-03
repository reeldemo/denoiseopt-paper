# Preflight checks for paper experiment launchers (sourced from experiment_env.sh).

# Reelsynth snapshot that still ships scripts/baselines/ (required by holdout_eval.py).
export REELSYNTH_PIN_COMMIT="${REELSYNTH_PIN_COMMIT:-0a8567b}"

N2N_CKPT_REL="brand/artifacts/n2n_seam_baselines/n2n_corrupt_corrupt.pt"
export N2N_CHECKPOINT="${REELSYNTH_ROOT}/${N2N_CKPT_REL}"

_experiment_preflight() {
  local err=0

  if [[ ! -d "${REELSYNTH_ROOT}/scripts/baselines" ]]; then
    echo "ERROR: REELSYNTH_ROOT is missing scripts/baselines/ (holdout_eval imports baselines.n2n_seam)." >&2
    echo "  Current REELSYNTH_ROOT=${REELSYNTH_ROOT}" >&2
    echo "  Pin reelsynth to commit ${REELSYNTH_PIN_COMMIT} (or newer snapshot that restores baselines/):" >&2
    echo "    git -C \"\${REELSYNTH_ROOT}\" fetch origin ${REELSYNTH_PIN_COMMIT}" >&2
    echo "    git -C \"\${REELSYNTH_ROOT}\" checkout ${REELSYNTH_PIN_COMMIT}" >&2
    echo "  See EXPERIMENT_PLAN.md § Environment." >&2
    err=1
  fi

  if [[ -z "${PAPER_PYTHON:-}" ]]; then
    echo "ERROR: PAPER_PYTHON must be set to a Python with PyTorch (CUDA venv recommended)." >&2
    echo "  export PAPER_PYTHON=/path/to/.venv/bin/python" >&2
    err=1
  elif ! "${PAPER_PYTHON}" -c "import torch" 2>/dev/null; then
    echo "ERROR: PAPER_PYTHON (${PAPER_PYTHON}) cannot import torch." >&2
    err=1
  fi

  if [[ "${SKIP_N2N_CKPT:-0}" != "1" && ! -f "${N2N_CHECKPOINT}" ]]; then
    echo "ERROR: Missing N2N baseline checkpoint (required for holdout scoring):" >&2
    echo "  ${N2N_CHECKPOINT}" >&2
    echo "  Copy the artifact from a machine that already trained it, or run (manual, ~3 h GPU on RTX 3060):" >&2
    echo "    ./scripts/run_n2n_baseline_retrain.sh" >&2
    err=1
  fi

  return "${err}"
}

if ! _experiment_preflight; then
  return 1 2>/dev/null || exit 1
fi
unset _experiment_preflight
