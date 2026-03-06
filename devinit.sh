#!/usr/bin/env bash
set -Eeuo pipefail

readonly SESSION_NAME="invest"
readonly ROOT_DIR="/mnt/c/00_mycode/Invest"
readonly PYTHON_DIR="${ROOT_DIR}/python"
readonly BACKEND_DIR="${ROOT_DIR}/backend"
readonly FRONTEND_DIR="${ROOT_DIR}/frontend"
readonly VENV_ACTIVATE="${PYTHON_DIR}/.venv/bin/activate"
readonly LOG_FILE="${ROOT_DIR}/backend.log"

die() {
  echo "devinit.sh: $*" >&2
  exit 1
}

escape() {
  printf '%q' "$1"
}

attach_or_switch() {
  if [[ -n "${TMUX:-}" ]]; then
    exec tmux switch-client -t "${SESSION_NAME}"
  fi
  exec tmux attach-session -t "${SESSION_NAME}"
}

validate_paths() {
  [[ -d "${ROOT_DIR}" ]] || die "root directory not found: ${ROOT_DIR}"
  [[ -d "${PYTHON_DIR}" ]] || die "python directory not found: ${PYTHON_DIR}"
  [[ -f "${VENV_ACTIVATE}" ]] || die "venv activation script not found: ${VENV_ACTIVATE}"
  [[ -d "${BACKEND_DIR}" ]] || die "backend directory not found: ${BACKEND_DIR}"
  [[ -d "${FRONTEND_DIR}" ]] || die "frontend directory not found: ${FRONTEND_DIR}"
}

create_layout() {
  tmux new-session -d -s "${SESSION_NAME}" -n dev -c "${ROOT_DIR}"
  tmux split-window -h -t "${SESSION_NAME}:0.0" -c "${ROOT_DIR}"
  tmux split-window -v -t "${SESSION_NAME}:0.0" -c "${ROOT_DIR}"
  tmux split-window -v -t "${SESSION_NAME}:0.1" -c "${ROOT_DIR}"
  tmux select-layout -t "${SESSION_NAME}:0" tiled

  tmux setw -t "${SESSION_NAME}:0" pane-border-status top
  tmux select-pane -t "${SESSION_NAME}:0.0" -T backend
  tmux select-pane -t "${SESSION_NAME}:0.1" -T frontend
  tmux select-pane -t "${SESSION_NAME}:0.2" -T copilot
  tmux select-pane -t "${SESSION_NAME}:0.3" -T logs
}

start_commands() {
  local backend_cmd frontend_cmd copilot_cmd logs_cmd

  backend_cmd="cd $(escape "${PYTHON_DIR}") && source $(escape "${VENV_ACTIVATE}") && cd $(escape "${BACKEND_DIR}") && python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000"
  frontend_cmd="cd $(escape "${PYTHON_DIR}") && source $(escape "${VENV_ACTIVATE}") && cd $(escape "${FRONTEND_DIR}") && npm run dev -- --host"
  copilot_cmd="cd $(escape "${PYTHON_DIR}") && source $(escape "${VENV_ACTIVATE}") && cd $(escape "${ROOT_DIR}") && copilot --model gpt-5.3-codex --yolo --autopilot --add-dir $(escape "${ROOT_DIR}")"
  logs_cmd="cd $(escape "${ROOT_DIR}") && tail -f $(escape "${LOG_FILE}")"

  tmux send-keys -t "${SESSION_NAME}:0.0" "${backend_cmd}" C-m
  tmux send-keys -t "${SESSION_NAME}:0.1" "${frontend_cmd}" C-m
  tmux send-keys -t "${SESSION_NAME}:0.2" "${copilot_cmd}" C-m
  tmux send-keys -t "${SESSION_NAME}:0.3" "${logs_cmd}" C-m
}

main() {
  command -v tmux >/dev/null 2>&1 || die "tmux is not installed."

  if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
    attach_or_switch
  fi

  validate_paths
  touch "${LOG_FILE}"
  create_layout
  start_commands
  attach_or_switch
}

main "$@"
