#!/usr/bin/env bash
# E1: ten eval-seed holdout (see EXPERIMENT_PLAN.md).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiment_env.sh
source "${SCRIPT_DIR}/experiment_env.sh"
# shellcheck source=experiment_helpers.sh
source "${SCRIPT_DIR}/experiment_helpers.sh"
export PYTHONPATH="${PAPER_ENGINE}:${PYTHONPATH:-}"
DRY=()
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY=(--dry-run)
  shift
fi
"${PAPER_PYTHON}" "${PAPER_ENGINE}/e1_holdout_10seed.py" "${DRY[@]}" "$@"
rc=$?
research_backup_step "E1"
exit "$rc"
