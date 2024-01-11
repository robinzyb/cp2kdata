import regex as re
import numpy as np

ATOMIC_FORCES_RE = re.compile(
    r"""
    \sATOMIC\sFORCES\sin\s\[a\.u\.\]\s*\n
    \n
    \s\#.+\n
    (
        \s+(?P<atom>\d+)
        \s+(?P<kind>\d+)
        \s+(?P<element>\w+)
        \s+(?P<x>[\s-]\d+\.\d+)
        \s+(?P<y>[\s-]\d+\.\d+)
        \s+(?P<z>[\s-]\d+\.\d+)
        \n
    )+
    """,
    re.VERBOSE
)


def parse_atomic_forces_list(output_file):
    atomic_forces_list = []
    for match in ATOMIC_FORCES_RE.finditer(output_file):
        atomic_forces = []
        for x, y, z in zip(*match.captures("x", "y", "z")):
            atomic_forces.append([x, y, z])
        atomic_forces_list.append(atomic_forces)
    if atomic_forces_list:
        return np.array(atomic_forces_list, dtype=float)
    else:
        return None
