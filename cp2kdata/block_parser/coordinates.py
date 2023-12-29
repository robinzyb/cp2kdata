import regex as re
import numpy as np

INIT_ATOMIC_COORDINATES_RE = re.compile(
    r"""
    \sMODULE\sQUICKSTEP:\s+ATOMIC\sCOORDINATES\sIN\sangstrom\s*\n
    \n
    \s+Atom\s+Kind\s+Element\s+X\s+Y\s+Z\s+Z\(eff\)\s+Mass\s*\n
    (\n)?
    (
        \s+(?P<atom>\d+)
        \s+(?P<kind>\d+)
        \s+(?P<element>\w+)
        \s+\d+
        \s+(?P<x>[-]?\d+\.\d+)
        \s+(?P<y>[-]?\d+\.\d+)
        \s+(?P<z>[-]?\d+\.\d+)
        \s+[-]?\d+\.\d+
        \s+[-]?\d+\.\d+
        \n
    )+
    """,
    re.VERBOSE | re.IGNORECASE,
)


def parse_init_atomic_coordinates(output_file):

    match = INIT_ATOMIC_COORDINATES_RE.search(output_file)
    # only get the first match
    init_atomic_coordinates = []
    chemical_symbols = []
    for x, y, z in zip(*match.captures("x", "y", "z")):
        init_atomic_coordinates.append([x, y, z])
    atom_kind_list = [int(kind) for kind in match.captures("kind")]
    chemical_symbols = match.captures("element")

    if init_atomic_coordinates:
        return np.array(init_atomic_coordinates, dtype=float), np.array(atom_kind_list, dtype=int), chemical_symbols
    else:
        return None
