# Shared environment for paper experiment launchers (source from run_e*.sh / queue_all.sh).
# No secrets — only paths and interpreter discovery.

_experiment_env_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
export PAPER_ROOT="$(cd "${_experiment_env_dir}/.." && pwd)"

if [[ -z "${REELSYNTH_ROOT:-}" ]]; then
  echo "ERROR: REELSYNTH_ROOT must be set (no default sibling path)." >&2
  echo "  export REELSYNTH_ROOT=/path/to/reelsynth" >&2
  unset _experiment_env_dir
  return 1 2>/dev/null || exit 1
fi

if [[ ! -d "${REELSYNTH_ROOT}/scripts" ]]; then
  echo "ERROR: REELSYNTH_ROOT must point at the reelsynth repo (with scripts/)." >&2
  echo "  export REELSYNTH_ROOT=/path/to/reelsynth" >&2
  unset _experiment_env_dir
  return 1 2>/dev/null || exit 1
fi

if [[ -x "${REELSYNTH_ROOT}/.venv_gpu/bin/python" ]]; then
  export ENGINE_PYTHON="${REELSYNTH_ROOT}/.venv_gpu/bin/python"
elif [[ -f "${REELSYNTH_ROOT}/.venv_gpu/Scripts/python.exe" ]]; then
  export ENGINE_PYTHON="${REELSYNTH_ROOT}/.venv_gpu/Scripts/python.exe"
else
  export ENGINE_PYTHON="${ENGINE_PYTHON:-python3}"
fi

if [[ -z "${PAPER_PYTHON:-}" ]]; then
  echo "ERROR: PAPER_PYTHON must be set (Python with torch for holdout_eval)." >&2
  echo "  export PAPER_PYTHON=/path/to/.venv/bin/python" >&2
  unset _experiment_env_dir
  return 1 2>/dev/null || exit 1
fi

export RESULTS_DIR="${PAPER_ROOT}/results"
export FIGURES_DIR="${PAPER_ROOT}/figures"
export REELSYNTH_ARTIFACTS_DIR="${REELSYNTH_ROOT}/brand/artifacts"
export QUEUE_STATUS="${RESULTS_DIR}/experiment_queue_status.json"

export ENGINE_SCRIPTS="${REELSYNTH_ROOT}/scripts"
export PAPER_ENGINE="${PAPER_ROOT}/scripts/engine"

# shellcheck source=experiment_preflight.sh
source "${_experiment_env_dir}/experiment_preflight.sh"
unset _experiment_env_dir
