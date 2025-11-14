#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"

if [ -e "$script_dir/../.venv/bin/activate" ]; then
  source "$script_dir/../.venv/bin/activate"
fi

isort \
  --quiet \
  --settings "$script_dir/../pyproject.toml" \
  --skip "${script_dir}/../.cache" \
  --skip "${script_dir}/../.venv" \
  ${check_args[@]+"${check_args[@]}"} \
  "$script_dir/.."

black \
  ${check_args[@]+"${check_args[@]}"} \
  "$script_dir/.."

mypy \
  --config-file "$script_dir/../pyproject.toml" \
  --cache-dir "$script_dir/../.mypy_cache" \
  "$script_dir/.."
