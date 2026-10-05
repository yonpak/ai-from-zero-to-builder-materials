#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 labs/notebooks/level-XX/script.py" >&2
  exit 2
fi

script="$1"
case "$script" in
  labs/notebooks/level-12/*.py|labs/notebooks/level-13/*.py|labs/notebooks/level-14/*.py|labs/notebooks/level-15/*.py)
    ;;
  *)
    echo "refusing path outside Level 12-15 notebook labs: $script" >&2
    exit 2
    ;;
esac

if [[ ! -f "$script" ]]; then
  echo "lab script not found: $script" >&2
  exit 2
fi

docker run --rm \
  -v "$PWD":/work \
  -w /work \
  python:3.11-slim \
  python "$script"
