import regex as re
import numpy as np


ATOMIC_KINDS_RE = re.compile(
    r"""
    \s+\d+\.\sAtomic\skind:\s+(?P<atomic_kind>\S+)
    """,
    re.VERBOSE
)

def parse_atomic_kinds(output_file):
    atomic_kinds = []
    for match in ATOMIC_KINDS_RE.finditer(output_file):
        atomic_kinds.append(match["atomic_kind"])
    if atomic_kinds:
        return np.array(atomic_kinds, dtype=str)
    else:
        return None