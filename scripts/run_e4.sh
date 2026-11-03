#!/usr/bin/env bash
# E4: hybrid branch ablations at ~5k budget × three search seeds.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiment_env.sh
source "${SCRIPT_DIR}/experiment_env.sh"
export PYTHONPATH="${PAPER_ENGINE}:${PYTHONPATH:-}"
DRY=()
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY=(--dry-run)
  shift
fi
exec "${PAPER_PYTHON}" "${PAPER_ENGINE}/e4_branch_ablation.py" "${DRY[@]}" "$@"
