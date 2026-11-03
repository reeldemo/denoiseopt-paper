#!/usr/bin/env bash
# E1: ten eval-seed holdout (see EXPERIMENT_PLAN.md).
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
exec "${PAPER_PYTHON}" "${PAPER_ENGINE}/e1_holdout_10seed.py" "${DRY[@]}" "$@"
