#!/usr/bin/env bash
# E3: matched 5k meta-compare on two extra search seeds (six approaches each).
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
"${PAPER_PYTHON}" "${PAPER_ENGINE}/e3_meta_extra_seeds.py" "${DRY[@]}" "$@"
rc=$?
research_backup_step "E3" || exit $?
exit "$rc"
