#!/usr/bin/env bash
# E2: FitCell-to-plateau hybrid converge on three search seeds + holdout eval.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for arg in "$@"; do
  if [[ "${arg}" == "--dry-run" ]]; then
    export RESEARCH_BACKUP_OPTIONAL=1
    break
  fi
done
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
"${PAPER_PYTHON}" "${PAPER_ENGINE}/e2_v14_converge.py" "${DRY[@]}" "$@"
rc=$?
research_backup_step "E2" || exit $?
exit "$rc"
