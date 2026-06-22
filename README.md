# 3-stage RISC-V Golden Generator

Generate ACT4/Sail golden files for the `3-stage_RISC-V` compliance runner.

## Target WSL Layout

Keep `~/risc-v` simple:

```text
~/risc-v/
  riscv-arch-test/                  # official ACT4 repo
  3-stage-riscv-golden-generator/    # this repo
```

The generator stores its ACT4 work cache inside:

```text
3-stage-riscv-golden-generator/.work/
```

## What This Repo Contains

```text
generate_golden.sh
config.env.example
act4_config/
env/
scripts/export_act4_to_repo.py
```

This repo does not contain ACT4, Sail, or the RISC-V toolchain.

## First-Time Setup

Clone ACT4 and this generator repo in WSL:

```bash
mkdir -p ~/risc-v
cd ~/risc-v
git clone https://github.com/riscv/riscv-arch-test.git
git clone https://github.com/WsWSC/3-stage-riscv-golden-generator.git 3-stage-riscv-golden-generator
```

Create local config:

```bash
cd ~/risc-v/3-stage-riscv-golden-generator
cp config.env.example config.env
```

Edit `config.env`:

```bash
TARGET_REPO=/mnt/c/Users/<windows_user>/Documents/3-stage_RISC-V
```

`TARGET_REPO` is the Windows `3-stage_RISC-V` repo path as seen from WSL.

## Required WSL Tools

These commands must work in WSL:

```bash
which mise
which riscv64-unknown-elf-gcc
which riscv64-unknown-elf-objdump
which riscv64-unknown-elf-objcopy
which sail_riscv_sim
```

If `sail_riscv_sim` is not in `PATH`, set it in `config.env`:

```bash
SAIL_RISCV_SIM=/path/to/sail_riscv_sim
```

## Generate Golden

```bash
cd ~/risc-v/3-stage-riscv-golden-generator
./generate_golden.sh
```

Generated files are exported to:

```text
$TARGET_REPO/sim/compliance_test/golden_sig/
$TARGET_REPO/sim/compliance_test/DUT_metadata/
$TARGET_REPO/sim/compliance_test/DUT_runtime/
```

Expected current RV32IM count:

```text
golden_sig/*.sig        47
DUT_metadata/*.json     47
DUT_runtime/bin/*.bin   47
DUT_runtime/data/*.data 47
```

## Local Files

Ignored local files:

```text
config.env
.work/
```
