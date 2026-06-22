# 3stage RISC-V Golden Generator

Generate ACT4/Sail golden files for the `3-stage_RISC-V` compliance runner.

## Layout

```text
3stage-riscv-golden-generator/
  generate_golden.sh
  config.env.example
  act4_config/
  env/
  scripts/export_act4_to_repo.py
```

## Setup

Clone ACT4 in WSL:

```bash
cd ~/risc-v
git clone https://github.com/riscv/riscv-arch-test.git
```

Prepare local config:

```bash
cd ~/risc-v/3stage-riscv-golden-generator
cp config.env.example config.env
```

Edit `config.env` and set `TARGET_REPO` to the Windows repo path as seen from WSL:

```bash
TARGET_REPO=/mnt/c/Users/<windows_user>/Documents/3-stage_RISC-V
```

Required WSL tools:

- `mise`
- `riscv64-unknown-elf-gcc`
- `riscv64-unknown-elf-objdump`
- `riscv64-unknown-elf-objcopy`
- `sail_riscv_sim`

## Generate

```bash
cd ~/risc-v/3stage-riscv-golden-generator
./generate_golden.sh
```

Output is exported to the Windows repo:

```text
sim/compliance_test/golden_sig/
sim/compliance_test/DUT_metadata/
sim/compliance_test/DUT_runtime/
```
