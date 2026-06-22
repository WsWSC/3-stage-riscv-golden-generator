#!/usr/bin/env bash
set -euo pipefail

GENERATOR_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CONFIG_FILE=${CONFIG_FILE:-$GENERATOR_ROOT/config.env}

if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
fi

RISCV_HOME=${RISCV_HOME:-$HOME/risc-v}
ACT4_REPO=${ACT4_REPO:-$RISCV_HOME/riscv-arch-test}
ACT4_WORK=${ACT4_WORK:-$GENERATOR_ROOT/.work/act4_work}
TARGET_REPO=${TARGET_REPO:-}
EXTENSIONS=${EXTENSIONS:-I M}
CONFIG=${CONFIG:-$GENERATOR_ROOT/act4_config/3stage-rv32im/test_config.yaml}

export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
SAIL_RISCV_SIM=${SAIL_RISCV_SIM:-$(command -v sail_riscv_sim || true)}

if [ -z "$TARGET_REPO" ]; then
    echo "missing TARGET_REPO" >&2
    echo "copy config.env.example to config.env and set TARGET_REPO=/mnt/c/.../3-stage_RISC-V" >&2
    exit 1
fi

if [ ! -d "$ACT4_REPO" ]; then
    echo "missing ACT4_REPO: $ACT4_REPO" >&2
    exit 1
fi

if [ -z "$SAIL_RISCV_SIM" ] || [ ! -x "$SAIL_RISCV_SIM" ]; then
    echo "missing sail_riscv_sim in PATH" >&2
    echo "install Sail or set SAIL_RISCV_SIM in config.env" >&2
    exit 1
fi

if [ ! -d "$TARGET_REPO" ]; then
    echo "missing TARGET_REPO: $TARGET_REPO" >&2
    exit 1
fi

export PATH="$(dirname "$SAIL_RISCV_SIM"):$PATH"

for ext in $EXTENSIONS; do
    cd "$ACT4_REPO"
    mise exec -- uv run act "$CONFIG" --workdir "$ACT4_WORK" --test-dir tests --extensions "$ext" --jobs 1 --debug --keep-going
done

cd "$GENERATOR_ROOT"
python3 scripts/export_act4_to_repo.py --act4-work "$ACT4_WORK/3stage-rv32im" --repo-root "$TARGET_REPO"
