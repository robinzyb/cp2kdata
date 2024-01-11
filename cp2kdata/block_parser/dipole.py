import regex as re
import numpy as np

DIPOLE_RE = re.compile(
    r"""
    \s{2}Dipole\smoment\s\[Debye\]\n
    \s{4}
    X=\s{,3}(?P<x>[\s-]\d+\.\d+)\s
    Y=\s{,3}(?P<y>[\s-]\d+\.\d+)\s
    Z=\s{,3}(?P<z>[\s-]\d+\.\d+)\s
    \s{4}Total=\s{,4}(?P<total>[\s-]\d+\.\d+)
    """,
    re.VERBOSE
)

# TODO write a pytest for this


def parse_dipole_list(output_file):
    dipole_list = []
    for match in DIPOLE_RE.finditer(output_file):
        for x, y, z, total in zip(*match.captures("x", "y", "z", "total")):
            dipole = [x, y, z, total]
        dipole_list.append(dipole)
    if dipole_list:
        return np.array(dipole_list, dtype=float)
    else:
        return None


"""
   Reference Point [Bohr]              0.00000000      0.00000000      0.00000000
   Charges
     Electronic=    864.00000000    Core=  -864.00000000    Total=     0.00000000
   Dipole vectors are based on the periodic (Berry phase) operator.
   They are defined modulo integer multiples of the cell matrix [Debye].
   [X] [   46.55265580     0.00000000     0.00000000 ] [i]
   [Y]=[    0.00000000    54.46353324     0.00000000 ]*[j]
   [Z] [    0.00000000     0.00000000    54.47313965 ] [k]
   Dipole moment [Debye]
     X=   -0.07183634 Y=   -0.07690441 Z=    1.13302571     Total=     1.13790246
"""
