import regex as re
import numpy as np

INIT_CELL_RE = re.compile(
    r"""
    \s+CELL\|\sVector\sa\s\[angstrom\]:
    \s+(?P<xx>[\s-]\d+\.\d+) 
    \s+(?P<xy>[\s-]\d+\.\d+) 
    \s+(?P<xz>[\s-]\d+\.\d+)
    \s+\|a\|\s+=\s+\S+
    \n
    \s+CELL\|\sVector\sb\s\[angstrom\]:
    \s+(?P<yx>[\s-]\d+\.\d+) 
    \s+(?P<yy>[\s-]\d+\.\d+) 
    \s+(?P<yz>[\s-]\d+\.\d+)
    \s+\|b\|\s+=\s+\S+
    \n
    \s+CELL\|\sVector\sc\s\[angstrom\]:
    \s+(?P<zx>[\s-]\d+\.\d+) 
    \s+(?P<zy>[\s-]\d+\.\d+) 
    \s+(?P<zz>[\s-]\d+\.\d+)
    \s+\|c\|\s+=\s+\S+
    \n
    """,
    re.VERBOSE
)

def parse_init_cell(output_file):
    init_cell = []
    for match in INIT_CELL_RE.finditer(output_file):
        init_cell = [
            [match["xx"], match["xy"], match["xz"]],
            [match["yx"], match["yy"], match["yz"]],
            [match["zx"], match["zy"], match["zz"]]
        ]

    if init_cell:
        return np.array(init_cell, dtype=float)
    else:
        return None