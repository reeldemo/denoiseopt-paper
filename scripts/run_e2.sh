#!/usr/bin/env bash
# E2: FitCell-to-plateau hybrid converge on three search seeds + holdout eval.
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
exec "${PAPER_PYTHON}" "${PAPER_ENGINE}/e2_v14_converge.py" "${DRY[@]}" "$@"
