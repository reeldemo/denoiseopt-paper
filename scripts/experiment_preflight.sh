# Preflight checks for paper experiment launchers (sourced from experiment_env.sh).

# Reelsynth snapshot that still ships scripts/baselines/ (required by holdout_eval.py).
export REELSYNTH_PIN_COMMIT="${REELSYNTH_PIN_COMMIT:-0a8567b}"

N2N_CKPT_REL="brand/artifacts/n2n_seam_baselines/n2n_corrupt_corrupt.pt"
export N2N_CHECKPOINT="${REELSYNTH_ROOT}/${N2N_CKPT_REL}"

_preflight_writable_dir() {
  local label="$1"
  local dir="$2"
  if [[ ! -d "${dir}" ]]; then
    echo "ERROR: ${label} must exist (not auto-created): ${dir}" >&2
    return 1
  fi
  if [[ ! -w "${dir}" ]]; then
    echo "ERROR: ${label} is not writable: ${dir}" >&2
    return 1
  fi
  return 0
}

_experiment_preflight() {
  local err=0
  local hook="${RESEARCH_BACKUP_HOOK:-${HOME}/bin/research-backup-now}"

  if ! _preflight_writable_dir "RESULTS_DIR" "${RESULTS_DIR}"; then
    err=1
  fi
  if ! _preflight_writable_dir "REELSYNTH brand/artifacts" "${REELSYNTH_ARTIFACTS_DIR}"; then
    err=1
  fi

  if [[ "${RESEARCH_BACKUP_OPTIONAL:-0}" != "1" ]]; then
    if [[ ! -x "${hook}" ]]; then
      echo "ERROR: mandatory backup hook missing or not executable: ${hook}" >&2
      echo "  Set RESEARCH_BACKUP_OPTIONAL=1 only for dry-run/CI." >&2
      err=1
    fi
  fi

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
unset _experiment_preflight _preflight_writable_dir
