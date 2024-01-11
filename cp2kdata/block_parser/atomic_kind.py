import regex as re
import numpy as np


NUM_ATOMIC_KINDS_RE = re.compile(
    r"""
    \s+-\sAtomic\skinds:\s+(?P<num_atomic_kind>\d+)
    """,
    re.VERBOSE
)
ATOMIC_KINDS_RE = re.compile(
    r"""
    \s{2}\d+\.\sAtomic\skind:\s+(?P<atomic_kind>\S+)
    """,
    re.VERBOSE
)


def parse_num_atomic_kinds(output_file):
    num_atomic_kinds_list = []

    for match in NUM_ATOMIC_KINDS_RE.finditer(output_file):
        num_atomic_kinds_list.append(int(match["num_atomic_kind"]))
    return num_atomic_kinds_list


def parse_atomic_kinds(output_file):
    num_atomic_kinds_list = parse_num_atomic_kinds(output_file)
    atomic_kinds = []
    for match in ATOMIC_KINDS_RE.finditer(output_file):
        atomic_kinds.append(match["atomic_kind"])
    if atomic_kinds:
        # only return the last atomic kinds
        return np.array(atomic_kinds[-num_atomic_kinds_list[-1]:], dtype=str)
    else:
        return None
