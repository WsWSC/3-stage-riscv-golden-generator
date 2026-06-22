import argparse
import json
import os
import shutil
import subprocess
import tempfile


INSTRUCTION_SECTIONS = {
    ".text.init",
    ".text.rvtest",
    ".text.rvmodel",
    ".text",
}

DATA_SECTION_FLAGS = {"ALLOC", "LOAD", "DATA"}
MEM_WORDS = 65536
MEM_BYTES = MEM_WORDS * 4
REPO_ROOT = None


def project_root():
    if REPO_ROOT:
        return REPO_ROOT

    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def compliance_dir():
    return os.path.join(project_root(), "sim", "compliance_test")


def run_cmd(cmd):
    return subprocess.check_output(cmd, text=True)


def parse_sections(elf):
    output = run_cmd(["riscv64-unknown-elf-objdump", "-h", elf])
    sections = []
    lines = output.splitlines()

    for index, line in enumerate(lines):
        parts = line.split()
        if len(parts) < 7 or not parts[0].isdigit():
            continue

        name = parts[1]
        size = int(parts[2], 16)
        addr = int(parts[3], 16)
        flags = set()
        if index + 1 < len(lines):
            flags = {item.strip() for item in lines[index + 1].split(",")}

        sections.append({"name": name, "size": size, "addr": addr, "flags": flags})

    return sections


def parse_symbols(elf):
    output = run_cmd(["riscv64-unknown-elf-nm", "-n", elf])
    symbols = {}

    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            symbols[parts[2]] = int(parts[0], 16)

    return symbols


def dump_section(elf, section_name):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.check_call(
            ["riscv64-unknown-elf-objcopy", "--dump-section", section_name + "=" + tmp_path, elf],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with open(tmp_path, "rb") as section_file:
            return section_file.read()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def section_in_range(section):
    return section["addr"] + section["size"] <= MEM_BYTES


def build_image(elf, sections):
    image = bytearray(MEM_BYTES)
    max_end = 0

    for section in sections:
        if section["size"] == 0:
            continue
        if not section_in_range(section):
            raise RuntimeError(
                section["name"] + " exceeds COMPLIANCE_MEM: "
                + hex(section["addr"] + section["size"])
            )

        data = dump_section(elf, section["name"])
        start = section["addr"]
        end = start + len(data)
        image[start:end] = data
        max_end = max(max_end, end)

    aligned_end = (max_end + 3) & ~3
    return image[:aligned_end]


def write_raw_image(path, image):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as out_file:
        out_file.write(image)


def write_word_image(path, image, pad_to_mem=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    padded = bytearray(image)
    if pad_to_mem:
        padded.extend([0] * (MEM_BYTES - len(padded)))
    while len(padded) % 4 != 0:
        padded.append(0)

    with open(path, "w", encoding="ascii") as out_file:
        for index in range(0, len(padded), 4):
            b0, b1, b2, b3 = padded[index:index + 4]
            out_file.write(bytearray([b3, b2, b1, b0]).hex() + "\n")


def is_instruction_section(section):
    return section["name"] in INSTRUCTION_SECTIONS and "CODE" in section["flags"]


def is_data_section(section):
    return (
        section["name"] not in INSTRUCTION_SECTIONS
        and DATA_SECTION_FLAGS.issubset(section["flags"])
    )


def test_name_from_elf(elf):
    name = os.path.basename(elf)
    if name.endswith(".elf"):
        name = name[:-4]
    return name


def find_elfs(elf_root):
    elfs = []
    for current_root, _, files in os.walk(elf_root):
        for filename in files:
            if filename.endswith(".elf"):
                elfs.append(os.path.join(current_root, filename))
    return sorted(elfs)


def require_symbol(symbols, primary, fallback=None):
    if primary in symbols:
        return symbols[primary]
    if fallback and fallback in symbols:
        return symbols[fallback]
    raise RuntimeError("missing symbol: " + primary)


def import_one(elf, build_root, args):
    rel_dir = os.path.relpath(os.path.dirname(elf), args.elf_root).replace("\\", "/")
    act_name = test_name_from_elf(elf)
    arch = rel_dir.split("/")[0]
    repo_name = arch + "-" + act_name

    sections = parse_sections(elf)
    symbols = parse_symbols(elf)

    inst_sections = [section for section in sections if is_instruction_section(section)]
    data_sections = [section for section in sections if is_data_section(section)]

    if not inst_sections:
        raise RuntimeError("missing instruction sections: " + elf)

    bin_path = os.path.join(compliance_dir(), "DUT_runtime", "bin", repo_name + ".bin")
    data_path = os.path.join(compliance_dir(), "DUT_runtime", "data", repo_name + ".data")
    ref_path = os.path.join(compliance_dir(), "golden_sig", repo_name + ".sig")
    meta_path = os.path.join(compliance_dir(), "DUT_metadata", repo_name + ".json")

    write_raw_image(bin_path, build_image(elf, inst_sections))
    write_word_image(data_path, build_image(elf, data_sections), pad_to_mem=True)

    ref_source = os.path.join(build_root, rel_dir, act_name + ".sig")
    if not os.path.exists(ref_source):
        raise RuntimeError("missing ACT4 signature: " + ref_source)
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    shutil.copyfile(ref_source, ref_path)

    metadata = {
        "name": repo_name,
        "source": rel_dir + "/" + act_name + ".S",
        "bin": os.path.relpath(bin_path, project_root()).replace("\\", "/"),
        "data": os.path.relpath(data_path, project_root()).replace("\\", "/"),
        "reference": os.path.relpath(ref_path, project_root()).replace("\\", "/"),
        "signature_start": format(require_symbol(symbols, "begin_signature", "rvtest_sig_begin"), "08x"),
        "signature_end": format(require_symbol(symbols, "end_signature", "rvtest_sig_end"), "08x"),
        "tohost_addr": format(require_symbol(symbols, "tohost"), "08x"),
        "timeout_cycles": args.timeout_cycles,
    }

    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, indent=2)
        meta_file.write("\n")

    return repo_name


def parse_args():
    parser = argparse.ArgumentParser(description="Import ACT4 ELF/signature outputs into sim/compliance_test.")
    parser.add_argument("--act4-work", required=True, help="ACT4 DUT work directory, for example .../act4_work/3stage-rv32im.")
    parser.add_argument("--repo-root", help="Repo root path when this script runs outside the repo.")
    parser.add_argument("--timeout-cycles", type=int, default=1000000)
    return parser.parse_args()


def main():
    global REPO_ROOT
    args = parse_args()
    if args.repo_root:
        REPO_ROOT = os.path.abspath(args.repo_root)

    args.elf_root = os.path.join(args.act4_work, "elfs")
    build_root = os.path.join(args.act4_work, "build")

    imported = []
    for elf in find_elfs(args.elf_root):
        imported.append(import_one(elf, build_root, args))

    print("imported ACT4 tests: " + str(len(imported)))
    for name in imported:
        print("  " + name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
