#!/usr/bin/env bash
set -Eeuo pipefail

readonly SESSION_NAME="invest"
readonly ROOT_DIR="${HOME}/code/Invest"

if [ ! -d "${ROOT_DIR}" ]; then
  echo "エラー: ~/code/Invest が存在しません" >&2
  exit 1
fi

cd "${ROOT_DIR}"

export LESS="-R"
export EDITOR=nano
export TERM=xterm-256color

# start ssh agent
if ! pgrep -u "$USER" ssh-agent > /dev/null; then
  eval "$(ssh-agent -s)"
fi

ssh-add -l >/dev/null 2>&1 || ssh-add ~/.ssh/id_ed25519

echo "Copilot CLI をスマホ表示向けモードで起動しています"

readonly PYTHON_DIR="${ROOT_DIR}/python"
readonly BACKEND_DIR="${ROOT_DIR}/backend"
readonly FRONTEND_DIR="${ROOT_DIR}/frontend"
readonly VENV_ACTIVATE="${PYTHON_DIR}/.venv/bin/activate"
readonly LOG_FILE="${ROOT_DIR}/backend.log"
readonly FRONTEND_LOG_FILE="${ROOT_DIR}/frontend.log"

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

session_is_healthy() {
  local pane_count titles expected_title

  window_name="$(tmux display-message -p -t ${SESSION_NAME}:0 '#W')"
  [[ "${window_name}" == "dev" ]] || return 1

  pane_count="$(tmux list-panes -t "${SESSION_NAME}:0" 2>/dev/null | wc -l | tr -d ' ')"
  [[ "${pane_count}" -eq 5 ]] || return 1

  titles="$(tmux list-panes -t "${SESSION_NAME}:0" -F '#{pane_title}' 2>/dev/null)"
  for expected_title in backend frontend copilot logs git; do
    grep -qx "${expected_title}" <<<"${titles}" || return 1
  done
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
  tmux set-option -g mouse on
  tmux set-option -g aggressive-resize on
  tmux set-option -g history-limit 50000
  tmux set-option -g remain-on-exit on
  tmux split-window -v -p 35 -t "${SESSION_NAME}:0.0" -c "${ROOT_DIR}"
  tmux split-window -h -t "${SESSION_NAME}:0.0" -c "${ROOT_DIR}"
  tmux split-window -h -t "${SESSION_NAME}:0.2" -c "${ROOT_DIR}"
  tmux split-window -h -t "${SESSION_NAME}:0.1" -c "${ROOT_DIR}"

  tmux setw -t "${SESSION_NAME}:0" pane-border-status top
  tmux select-pane -t "${SESSION_NAME}:0.0" -T backend
  tmux select-pane -t "${SESSION_NAME}:0.2" -T frontend
  tmux select-pane -t "${SESSION_NAME}:0.3" -T copilot
  tmux select-pane -t "${SESSION_NAME}:0.1" -T logs
  tmux select-pane -t "${SESSION_NAME}:0.4" -T git
  tmux select-pane -t "${SESSION_NAME}:0.3"
}

start_commands() {
  local backend_cmd frontend_cmd copilot_cmd logs_cmd git_cmd

  backend_cmd="cd ${PYTHON_DIR} && source ${VENV_ACTIVATE} && cd ${BACKEND_DIR} && while true; do python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee -a ${LOG_FILE}; echo \"backend crashed. restarting...\"; sleep 2; done"
  frontend_cmd="cd ${PYTHON_DIR} && source ${VENV_ACTIVATE} && cd ${FRONTEND_DIR} && while true; do npm run dev -- --host 0.0.0.0 --port 3000 --strictPort 2>&1 | tee -a ${FRONTEND_LOG_FILE}; echo \"frontend crashed. restarting...\"; sleep 2; done"
  copilot_cmd="cd $(escape "${PYTHON_DIR}") && source $(escape "${VENV_ACTIVATE}") && cd $(escape "${ROOT_DIR}") && copilot --model gpt-5-mini --autopilot --yolo --allow-all --add-github-mcp-toolset all --add-dir ~/code/Invest"
  logs_cmd="cd ${ROOT_DIR} && multitail ${LOG_FILE} ${FRONTEND_LOG_FILE}"
  git_cmd="cd ${ROOT_DIR} && echo 'Launching lazygit...' && lazygit"

  tmux send-keys -t "${SESSION_NAME}:0.0" "${backend_cmd}" C-m
  tmux send-keys -t "${SESSION_NAME}:0.2" "${frontend_cmd}" C-m
  tmux send-keys -t "${SESSION_NAME}:0.3" "${copilot_cmd}" C-m
  tmux send-keys -t "${SESSION_NAME}:0.1" "${logs_cmd}" C-m
  tmux send-keys -t "${SESSION_NAME}:0.4" "${git_cmd}" C-m
}

main() {
  local current_tmux_session=""

  command -v tmux >/dev/null 2>&1 || die "tmux is not installed."
  command -v lazygit >/dev/null 2>&1 || die "lazygit is not installed."

  if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
    if session_is_healthy; then
      attach_or_switch
    fi

    if [[ -n "${TMUX:-}" ]]; then
      current_tmux_session="$(tmux display-message -p '#S' 2>/dev/null || true)"
      [[ "${current_tmux_session}" != "${SESSION_NAME}" ]] || die "existing '${SESSION_NAME}' session is unhealthy in current tmux client; detach first and rerun to recreate it."
    fi

    echo "既存 tmux セッション(${SESSION_NAME}) が不完全なため再作成します"
    tmux kill-session -t "${SESSION_NAME}"
  fi

  validate_paths
  touch "${LOG_FILE}"
  touch "${FRONTEND_LOG_FILE}"
  create_layout
  start_commands
  attach_or_switch
}

main "$@"
