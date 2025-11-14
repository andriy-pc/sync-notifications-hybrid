#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"

if [ -e "$script_dir/../.venv/bin/activate" ]; then
  source "$script_dir/../.venv/bin/activate"
fi

min_coverage=80

while [[ $# -gt 0 ]]; do
    case $1 in
        --min-coverage=*)
            min_coverage="${1#*=}"
            if ! [[ "$min_coverage" =~ ^[0-9]+$ ]] || [ "$min_coverage" -gt 100 ] || [ "$min_coverage" -lt 0 ]; then
                echo "Error: min-coverage must be a number between 0 and 100"
                exit 1
            fi
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "\nRunning tests"
cd "$script_dir/.." && \
  pytest tests -svv \
  --disable-warnings \
  --cov-fail-under=$min_coverage \
  --cov="$script_dir/../." \
  --cov-config="$script_dir/../pyproject.toml"

echo -e "\nXML coverage report"
cd "$script_dir/.." && \
  coverage xml

echo -e "\nHTML coverage report"
cd "$script_dir/.." && \
  coverage html

