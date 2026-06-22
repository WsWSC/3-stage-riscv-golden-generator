# 3-stage RISC-V Golden Generator

This repo generates ACT4/Sail golden files for the 3-stage RV32IM CPU
compliance flow.

The CPU repo explains how to set up and run the compliance test flow. This repo
documents the generator-side files, settings, and generated outputs.

## Repository Layout

```text
generate_golden.sh      # Main generator entry point
config.env.example      # Local config template

act4_config/            # ACT4 config for the 3-stage RV32IM target
env/                    # ACT4 DUT environment files
scripts/                # Export helpers

.work/                  # Generated ACT4 work/cache directory
config.env              # Local config, copied from config.env.example
```

`config.env` and `.work/` are local generated files and should not be committed.

## Flow Roles

| Item | Role |
| --- | --- |
| `riscv-arch-test` | Official ACT4 tests and framework. |
| `3-stage-riscv-golden-generator` | Provides target config, DUT env files, and export logic. |
| `sail_riscv_sim` | Reference model that produces golden signatures. |
| `TARGET_REPO` | CPU repo that receives generated compliance files. |
| CPU repo `sim/compliance_test/` | Runs DUT simulation and compares against generated signatures. |

## Generator Files

| Path | Description |
| --- | --- |
| `generate_golden.sh` | Loads `config.env`, runs ACT4, and exports output to `TARGET_REPO`. |
| `config.env.example` | Template for local paths and generation options. |
| `act4_config/3stage-rv32im/test_config.yaml` | ACT4 target config used for this CPU. |
| `env/link.ld` | Linker script used when ACT4 builds tests. |
| `env/rvmodel_macros.h` | ACT4 DUT macro definitions. |
| `env/rvtest_config.h` | ACT4 test environment config. |
| `scripts/export_act4_to_repo.py` | Converts ACT4 output into the CPU repo compliance layout. |

## config.env

| Setting | Description |
| --- | --- |
| `TARGET_REPO` | CPU repo path that receives generated files. |
| `RISCV_HOME` | Parent folder for external RISC-V repos. Default: `$HOME/risc-v`. |
| `ACT4_REPO` | Path to the official `riscv-arch-test` repo. |
| `ACT4_WORK` | ACT4 build/cache folder. Default: `$GENERATOR_ROOT/.work/act4_work`. |
| `SAIL_RISCV_SIM` | Optional path to `sail_riscv_sim` if it is not in `PATH`. |
| `EXTENSIONS` | ACT4 extensions to generate. Default: `I M`. |

Example `TARGET_REPO` values:

```bash
# Windows repo as seen from WSL
TARGET_REPO=/mnt/c/Users/<windows_user>/Documents/3-stage_RISC-V

# CPU repo stored inside WSL
TARGET_REPO=$HOME/risc-v/3-Stage-RV32IM-RISC-V-CPU
```

To generate files for another CPU repo, change `TARGET_REPO` and rerun the
generator.

## Generated Output

Generated files are written under:

```text
$TARGET_REPO/sim/compliance_test/
```

| Output | Description |
| --- | --- |
| `golden_sig/*.sig` | Sail golden signatures. |
| `DUT_metadata/*.json` | Per-test signature range and runtime metadata. |
| `DUT_runtime/bin/*.bin` | Test binaries loaded by the DUT runner. |
| `DUT_runtime/data/*.data` | Data RAM initialization files. |

Expected current RV32IM count:

| Output group | Count |
| --- | ---: |
| `golden_sig/*.sig` | 47 |
| `DUT_metadata/*.json` | 47 |
| `DUT_runtime/bin/*.bin` | 47 |
| `DUT_runtime/data/*.data` | 47 |

## Command Summary

The CPU repo README owns the full setup flow. Generator-side commands are:

```bash
cp config.env.example config.env
# edit TARGET_REPO in config.env
./generate_golden.sh
```

`generate_golden.sh` performs these steps:

| Step | Description |
| --- | --- |
| 1 | Load `config.env`. |
| 2 | Check required paths and `sail_riscv_sim`. |
| 3 | Run ACT4 for each configured extension. |
| 4 | Keep ACT4 intermediate files under `.work/`. |
| 5 | Export signatures, metadata, binaries, and data images to `TARGET_REPO`. |

## Common Failures

| Message / Symptom | Fix |
| --- | --- |
| `missing TARGET_REPO` | Create `config.env` and set `TARGET_REPO`. |
| `missing ACT4_REPO` | Check that `ACT4_REPO` points to `riscv-arch-test`. |
| `sail_riscv_sim` not found | Add it to `PATH`, or set `SAIL_RISCV_SIM`. |
| `mise` not found | Install `mise` in WSL and reopen the shell. |
| `ACT4 requires GCC 15 or later` | If RISC-V GCC is 14.x, set `REQUIRED_GCC_MAJOR_VERSION = 14` in `riscv-arch-test/framework/src/act/config.py`, then rerun the generator. |
| Stale golden files | Rerun `./generate_golden.sh`. |
