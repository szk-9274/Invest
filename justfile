set shell := ["bash", "-cu"]

dev:
  ./devinit.sh

stop:
  tmux kill-session -t minervilism

logs:
  tail -F backend.log frontend.log

test:
  cd python && source .venv/bin/activate && pytest

lint:
  cd python && source .venv/bin/activate && ruff check .

fmt:
  cd python && source .venv/bin/activate && ruff format .
