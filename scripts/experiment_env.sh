# Shared environment for paper experiment launchers (source from run_e*.sh / queue_all.sh).
# No secrets — only paths and interpreter discovery.

_experiment_env_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
export PAPER_ROOT="$(cd "${_experiment_env_dir}/.." && pwd)"
export REELSYNTH_ROOT="${REELSYNTH_ROOT:-$(cd "${PAPER_ROOT}/../reelsynth" 2>/dev/null && pwd)}"
unset _experiment_env_dir

if [[ -z "${REELSYNTH_ROOT}" || ! -d "${REELSYNTH_ROOT}/scripts" ]]; then
  echo "ERROR: REELSYNTH_ROOT must point at the reelsynth repo (with scripts/)." >&2
  echo "  export REELSYNTH_ROOT=/path/to/reelsynth" >&2
  return 1 2>/dev/null || exit 1
fi

if [[ -x "${REELSYNTH_ROOT}/.venv_gpu/bin/python" ]]; then
  export ENGINE_PYTHON="${REELSYNTH_ROOT}/.venv_gpu/bin/python"
elif [[ -f "${REELSYNTH_ROOT}/.venv_gpu/Scripts/python.exe" ]]; then
  export ENGINE_PYTHON="${REELSYNTH_ROOT}/.venv_gpu/Scripts/python.exe"
else
  export ENGINE_PYTHON="${ENGINE_PYTHON:-python3}"
fi

export PAPER_PYTHON="${PAPER_PYTHON:-python3}"
export RESULTS_DIR="${PAPER_ROOT}/results"
export FIGURES_DIR="${PAPER_ROOT}/figures"
export QUEUE_STATUS="${RESULTS_DIR}/experiment_queue_status.json"
mkdir -p "${RESULTS_DIR}"

export ENGINE_SCRIPTS="${REELSYNTH_ROOT}/scripts"
export PAPER_ENGINE="${PAPER_ROOT}/scripts/engine"
