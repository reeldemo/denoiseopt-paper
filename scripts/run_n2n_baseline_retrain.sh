#!/usr/bin/env bash
# Optional: train primary corrupt→corrupt SeamN2N baseline under reelsynth (NOT run by queue_all).
#
# Requires REELSYNTH_ROOT at commit with scripts/baselines/ (see REELSYNTH_PIN_COMMIT in preflight).
# Default training: 20k steps, batch 64 — ~155 s on published RTX 3090 log for n2n_corrupt_corrupt only;
# budget ~2.5–3 h on RTX 3060 if CUDA is healthy (both modes ~5 h).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export SKIP_N2N_CKPT=1
# shellcheck source=experiment_env.sh
source "${SCRIPT_DIR}/experiment_env.sh"
# shellcheck source=experiment_helpers.sh
source "${SCRIPT_DIR}/experiment_helpers.sh"

TRAIN="${REELSYNTH_ROOT}/scripts/train_n2n_seam_baseline.py"
if [[ ! -f "${TRAIN}" ]]; then
  echo "ERROR: missing ${TRAIN}" >&2
  exit 1
fi

MODES="${1:-n2n_corrupt_corrupt}"
echo "== N2N baseline retrain modes=${MODES} ENGINE_PYTHON=${ENGINE_PYTHON}"
"${ENGINE_PYTHON}" "${TRAIN}" --modes "${MODES}" "$@"
research_backup_step "n2n_baseline_retrain"

if [[ ! -f "${N2N_CHECKPOINT}" ]]; then
  echo "ERROR: expected checkpoint after train: ${N2N_CHECKPOINT}" >&2
  exit 1
fi
echo "OK: ${N2N_CHECKPOINT}"
