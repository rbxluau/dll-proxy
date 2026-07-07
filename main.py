import argparse
from pathlib import Path
import shlex
import shutil
import subprocess
import uuid

import pefile


def get_comments(dll: Path):
    comments = []
    with pefile.PE(shutil.copy2(args.dll, dll)) as pe:
        if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
            for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                if symbol.name:
                    symbol_name = symbol.name.decode("utf-8", errors="ignore")
                    export = f"{symbol_name}={dll.stem}.{symbol_name},@{symbol.ordinal}"
                else:
                    export = f"_{symbol.ordinal}={dll.stem}.#{symbol.ordinal},@{symbol.ordinal},NONAME"
                comments.append(f'#pragma comment(linker, "/export:{export}")')
    return "\n".join(comments)


parser = argparse.ArgumentParser(description="DLL Proxy Toolchain")
parser.add_argument(
    "-d", "--dll", required=True, type=Path, help="Path to the DLL file"
)
parser.add_argument(
    "-b", "--bin", required=True, type=Path, help="Path to the BIN file"
)
parser.add_argument(
    "-o",
    "--ollvm",
    nargs="?",
    const=[
        "-mllvm",
        "-fla",
        "-mllvm",
        "-bcf",
        "-mllvm",
        "-bcf_prob=80",
        "-mllvm",
        "-bcf_loop=3",
        "-mllvm",
        "-sobf",
        "-mllvm",
        "-icall",
        "-mllvm",
        "-ibr",
        "-mllvm",
        "-igv",
        "-mllvm",
        "-sub",
        "-mllvm",
        "-sub_loop=3",
        "-mllvm",
        "-split",
        "-mllvm",
        "-split_num=5",
    ],
    default=[],
    type=shlex.split,
    help="Enable OLLVM (default: all protections, optional custom flags)",
)

args = parser.parse_args()
build_dir = Path("build")
build_dir.mkdir(exist_ok=True)

source_path = build_dir / f"{args.dll.stem}.cpp"
source_path.write_text(
    Path("dllmain.cpp")
    .read_text(encoding="utf-8")
    .replace(
        "{PRAGMA_COMMENTS}", get_comments(build_dir / f"{uuid.uuid4().hex[:8]}.dll")
    )
    .replace("{PAYLOAD_DATA}", "".join(f"\\x{b:02x}" for b in args.bin.read_bytes())),
    encoding="utf-8",
)

subprocess.run(
    ["clang-cl", "/LD", source_path.name, f"/Fe:{args.dll.name}"] + args.ollvm,
    cwd=build_dir,
)
