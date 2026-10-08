#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export UV_CACHE_DIR="$project_root/.uv-cache"
export UV_PYTHON_INSTALL_DIR="$project_root/.tools/python"
exec "$project_root/.tools/uv" "$@"

