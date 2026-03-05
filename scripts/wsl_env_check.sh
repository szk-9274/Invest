#!/usr/bin/env bash
set -euo pipefail

out="./wsl_env_report.txt"

echo "Collecting WSL environment info" > "$out"

echo "--- uname -a ---" >> "$out"
uname -a >> "$out" 2>&1 || true

echo "--- lsb_release -a ---" >> "$out"
lsb_release -a >> "$out" 2>&1 || true

echo "--- python version ---" >> "$out"
python3 --version >> "$out" 2>&1 || python --version >> "$out" 2>&1 || true

echo "--- pip freeze ---" >> "$out"
python3 -m pip freeze >> "$out" 2>&1 || python -m pip freeze >> "$out" 2>&1 || true

echo "--- node / npm versions ---" >> "$out"
node --version >> "$out" 2>&1 || true
npm --version >> "$out" 2>&1 || true

echo "--- npm top-level packages ---" >> "$out"
npm ls --depth=0 >> "$out" 2>&1 || true

echo "--- dpkg: system packages that may be needed ---" >> "$out"
for pkg in libxml2-dev libxslt1-dev python3-dev build-essential libssl-dev pkg-config libfreetype6-dev libpng-dev; do
  echo "Checking $pkg" >> "$out"
  dpkg -l "$pkg" >> "$out" 2>&1 || echo "$pkg: not installed" >> "$out"
done

echo "--- pip check (package conflicts) ---" >> "$out"
python3 -m pip check >> "$out" 2>&1 || true

echo "WSL env report written to: $out" >> "$out"
