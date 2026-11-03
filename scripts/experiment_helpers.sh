# Shared helpers for experiment launchers (source after experiment_env.sh).

research_backup_step() {
  local step="${1:?step name required}"
  local hook="${HOME}/bin/research-backup-now"
  if [[ -x "${hook}" ]]; then
    "${hook}" "${step}"
  fi
}
