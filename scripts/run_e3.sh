#!/usr/bin/env bash
# E3: matched 5k meta-compare on two extra search seeds (six approaches each).
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
exec "${PAPER_PYTHON}" "${PAPER_ENGINE}/e3_meta_extra_seeds.py" "${DRY[@]}" "$@"
