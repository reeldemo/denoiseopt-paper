#!/usr/bin/env bash
# Preflight tests: writable dirs + mandatory backup hook (no auto-created paths).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

FAKE_PY="${TMP}/fake-python"
cat >"${FAKE_PY}" <<'EOF'
#!/usr/bin/env bash
if [[ "${1:-}" == "-c" ]] && [[ "${2:-}" == *torch* ]]; then
  exit 0
fi
exec python3 "$@"
EOF
chmod +x "${FAKE_PY}"

RS="${TMP}/reelsynth"
PAPER="${TMP}/paper"
mkdir -p "${RS}/scripts/baselines" "${RS}/brand/artifacts/n2n_seam_baselines"
mkdir -p "${PAPER}/results"
touch "${RS}/brand/artifacts/n2n_seam_baselines/n2n_corrupt_corrupt.pt"

export REELSYNTH_ROOT="${RS}"
export RESULTS_DIR="${PAPER}/results"
export REELSYNTH_ARTIFACTS_DIR="${RS}/brand/artifacts"
export PAPER_PYTHON="${FAKE_PY}"
export SKIP_N2N_CKPT=0
export RESEARCH_BACKUP_OPTIONAL=1
export N2N_CHECKPOINT="${RS}/brand/artifacts/n2n_seam_baselines/n2n_corrupt_corrupt.pt"

# shellcheck source=../experiment_preflight.sh
if ! source "${ROOT}/experiment_preflight.sh"; then
  echo "FAIL: preflight should pass with optional backup and dirs present" >&2
  exit 1
fi
echo "ok preflight_passes_with_dirs"

rm -rf "${PAPER}/results"
if source "${ROOT}/experiment_preflight.sh" 2>/dev/null; then
  echo "FAIL: expected failure when RESULTS_DIR missing" >&2
  exit 1
fi
echo "ok fails_missing_results_dir"

mkdir -p "${PAPER}/results"
unset RESEARCH_BACKUP_OPTIONAL
if source "${ROOT}/experiment_preflight.sh" 2>/dev/null; then
  echo "FAIL: expected failure when backup hook missing and not optional" >&2
  exit 1
fi
echo "ok fails_missing_backup_hook"

echo "experiment_preflight tests passed"
