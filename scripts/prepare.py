#!/usr/bin/env python3
import argparse
from itertools import product
import fileinput
import os
import shutil
import subprocess
import sys

BOLD = "\033[1;37m"
NORMAL = "\033[0m"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_cmd(*args: str) -> None:
    subprocess.run(args, check=True, stderr=sys.stdout)


def _run_pipeline_to_file(commands: list[list[str]], output_path: str) -> None:
    """Stream commands through a pipeline, writing final stdout to output_path."""
    processes = []
    previous = None
    out_file = None
    try:
        for i, cmd in enumerate(commands):
            stdin = previous.stdout if previous else None
            if i == len(commands) - 1:
                out_file = open(output_path, "wb")
                current = subprocess.Popen(
                    cmd, stdin=stdin, stdout=out_file, stderr=sys.stdout
                )
            else:
                current = subprocess.Popen(
                    cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=sys.stdout
                )

            if previous and previous.stdout:
                previous.stdout.close()
            processes.append(current)
            previous = current

        for process in processes:
            return_code = process.wait()
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, process.args)
    finally:
        if out_file:
            out_file.close()


def strip_ext(files, ext):
    return [f[: -len(ext)] for f in filter(lambda f: f.endswith(ext), files)]


class Preparer:
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        mcrl2_path: str | None
    ) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.mcrl2_path = mcrl2_path

    def _find_tool(self, name: str, tool_path: str | None) -> str:
        search = os.pathsep.join(p for p in [tool_path, os.environ.get("PATH", "")] if p)
        path = shutil.which(name, path=search or None)
        if path is None:
            raise RuntimeError(f"Required tool not found: {name}")
        return path

    def _find_mcrl2_tool(self, name: str) -> str:
        return self._find_tool(name, self.mcrl2_path)

    def gen_abp(self, data: int, version: str) -> None:
        target = os.path.join(self.output_dir, f"abp_{data}-{version}.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"data{data}.mcrl2 abp.mcrl2 abp-{version}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"abp_{data}-{version}.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_cmd(self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target, lps_target)

    def gen_onebit(self, data: int, version: str) -> None:
        target = os.path.join(self.output_dir, f"onebit_{data}-{version}.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"data{data}.mcrl2 onebit.mcrl2 onebit-{version}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"onebit_{data}-{version}.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_cmd(self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target, lps_target)

    def gen_brp(self, data: int, llen: int, retries: int, version: str) -> None:
        target = os.path.join(self.output_dir, f"brp_{data}_{llen}_{retries}-{version}.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"data{data}.mcrl2 l{llen}.mcrl2 n{retries}.mcrl2 brp.mcrl2 brp-{version}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"brp_{data}_{llen}_{retries}-{version}.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_cmd(self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target, lps_target)

    def gen_swp(self, data: int, window: int, version: str) -> None:
        target = os.path.join(self.output_dir, f"swp_{data}_{window}-{version}.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"data{data}.mcrl2 n{window}.mcrl2 swp.mcrl2 swp-{version}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"swp_{data}_{window}-{version}.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_cmd(self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target, lps_target)

    def gen_dkr(self, ring: int, version: str) -> None:
        target = os.path.join(self.output_dir, f"dkr_{ring}-{version}.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"n{ring}.mcrl2 triple_channel.mcrl2 dkr.mcrl2 leader{ring}.mcrl2 leader-{version}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"dkr_{ring}-{version}.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_cmd(self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target, lps_target)

    def gen_franklin(self, ring: int, llen: int, version: str) -> None:
        target = os.path.join(self.output_dir, f"franklin_{ring}_{llen}-{version}.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"n{ring}.mcrl2 l{llen}.mcrl2 triple_channel.mcrl2 franklin.mcrl2 leader{ring}.mcrl2 leader-{version}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"franklin_{ring}_{llen}-{version}.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_cmd(self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target, lps_target)

    def gen_hesselink(self, data: int, version: str) -> None:
        target = os.path.join(self.output_dir, f"hesselink_{data}-{version}.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"data{data}.mcrl2 hesselink-{version}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"hesselink_{data}-{version}.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_cmd(self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target, lps_target)

    def gen_WMS(self) -> None:
        lps_target = os.path.join(self.output_dir, "WMS.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}{NORMAL}")
            _run_pipeline_to_file(
                [
                    [
                        self._find_mcrl2_tool("mcrl22lps"),
                        "-Dfvn",
                        os.path.join(self.input_dir, "WMS.mcrl2"),
                    ],
                    [self._find_mcrl2_tool("lpsconstelm"), "-v"],
                ],
                lps_target,
            )

    def gen_ertms(self) -> None:
        lps_target = os.path.join(self.output_dir, "ertms-b.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}{NORMAL}")
            _run_pipeline_to_file(
                [
                    [
                        self._find_mcrl2_tool("mcrl22lps"),
                        "-Dfvn",
                        os.path.join(self.input_dir, "INESS_iter1_r468.mcrl2"),
                    ],
                    [self._find_mcrl2_tool("lpsconstelm"), "-v"],
                    [self._find_mcrl2_tool("lpsparelm"), "-v"],
                ],
                lps_target,
            )

    def gen_lhc(self, num: int) -> None:
        target = os.path.join(self.output_dir, f"lhc_{num}-b.mcrl2")

        if not os.path.isfile(target):
            print(f"{BOLD}Generating {target}...{NORMAL}")
            sources = [
                os.path.join(self.input_dir, f)
                for f in f"data.mcrl2 act.mcrl2 sector.mcrl2 chamber.mcrl2 wheel.mcrl2 wheel_tm.mcrl2 Composition.mcrl2 initWheel{num}.mcrl2".split()
            ]
            with open(target, "w") as out:
                out.writelines(fileinput.input(sources))

        lps_target = os.path.join(self.output_dir, f"lhc_{num}-b.lps")

        if not os.path.isfile(lps_target):
            print(f"{BOLD}Generating {lps_target}...{NORMAL}")
            _run_pipeline_to_file(
                [
                    [self._find_mcrl2_tool("mcrl22lps"), "-Dfvn", target],
                    [self._find_mcrl2_tool("lpsconstelm"), "-v"],
                    [self._find_mcrl2_tool("lpsparelm"), "-v"],
                ],
                lps_target,
            )

    def prepare(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

        for d, v in product([2, 3, 4], ["b", "e"]):
            self.gen_abp(d, v)

        for d, v in product([2, 3, 4], ["b", "e"]):
            self.gen_onebit(d, v)

        for d, llen, n, v in product([2, 3, 4], [3, 4], [3, 4], ["b", "e"]):
            self.gen_brp(d, llen, n, v)

        for d, w, v in product([2, 3, 4], [2, 3, 4], ["b", "e"]):
            self.gen_swp(d, w, v)

        for r, v in product([2, 3, 4, 5], ["b", "e"]):
            self.gen_dkr(r, v)

        for r, llen, v in product([2, 3, 4, 5], [2, 3, 4, 5], ["b", "e"]):
            if r >= llen:
                self.gen_franklin(r, llen, v)

        for d, v in product([2, 3, 4, 5], ["b", "e"]):
            self.gen_hesselink(d, v)

        self.gen_WMS()

        for s in [2, 3, 4]:
            self.gen_lhc(s)

        self.gen_ertms()

    def generate_all(self, files) -> None:
        files = strip_ext(list(set(files)), ".lps")
        for m in files:
            lps_file = m + ".lps"
            sym_file = m + ".sym"

            if not os.path.isfile(sym_file):
                print("Generating {}...".format(sym_file))
                result = subprocess.run(
                    [self._find_mcrl2_tool("lpsreach"), "-v", lps_file, sym_file],
                    stdout=sys.stdout,
                    stderr=sys.stdout,
                    check=True,
                )
                if result.returncode != 0:
                    print("Error")
            if not os.path.isfile(sym_file):
                print("File {} could not be generated!".format(sym_file))
                continue


if __name__ == "__main__":
    default_input = os.path.join(SCRIPT_DIR, "..", "cases")
    default_output = os.path.join(SCRIPT_DIR, "..", "output")

    parser = argparse.ArgumentParser(
        description="Generate mCRL2 LPS files for all benchmark cases."
    )
    parser.add_argument(
        "--input-dir",
        default=default_input,
        help="Directory containing source .mcrl2 files (default: ../cases)",
    )
    parser.add_argument(
        "--output-dir",
        default=default_output,
        help="Directory for generated files (default: ../output)",
    )
    parser.add_argument(
        "--mcrl2-path",
        default=None,
        help="Directory containing mCRL2 tools (searched before PATH)",
    )
    args = parser.parse_args()

    preparer = Preparer(
        os.path.abspath(args.input_dir),
        os.path.abspath(args.output_dir),
        args.mcrl2_path,
    )
    preparer.prepare()
    preparer.generate_all(map(lambda f: os.path.join(args.output_dir, f), os.listdir(args.output_dir)))
