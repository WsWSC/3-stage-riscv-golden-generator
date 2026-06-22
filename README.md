# 3stage RISC-V Golden Generator

Generate ACT4/Sail golden files for the `3-stage_RISC-V` compliance runner.

## Directory Layout

```text
~/risc-v/
  riscv-arch-test/                  # official ACT4 repo
  tools/                            # RISC-V toolchain and Sail
  arch-test-compile/                # ACT4 workdir/cache
  3stage-riscv-golden-generator/    # this repo
```

## What This Repo Does

This repo does not contain ACT4, Sail, or the RISC-V toolchain.

It only contains the 3-stage CPU golden-generation recipe:

```text
generate_golden.sh
config.env.example
act4_config/
env/
scripts/export_act4_to_repo.py
```

## First-Time Setup

Clone ACT4 and this generator repo in WSL:

```bash
cd ~/risc-v
git clone https://github.com/riscv/riscv-arch-test.git
git clone https://github.com/WsWSC/3-stage-riscv-golden-generator.git
```

Create local config:

```bash
cd ~/risc-v/3-stage-riscv-golden-generator
cp config.env.example config.env
```

Edit only this line in `config.env`:

```bash
TARGET_REPO=/mnt/c/Users/<windows_user>/Documents/3-stage_RISC-V
```

`TARGET_REPO` is the Windows `3-stage_RISC-V` repo path as seen from WSL.

## Required WSL Tools

```bash
which mise
which riscv64-unknown-elf-gcc
which riscv64-unknown-elf-objdump
which riscv64-unknown-elf-objcopy
which sail_riscv_sim
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

`config.env` is local only and ignored by Git.
