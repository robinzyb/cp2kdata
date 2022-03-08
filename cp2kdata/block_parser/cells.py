import regex as re
import numpy as np

ALL_CELL_RE = re.compile(
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

def parse_all_cells(output_file):
    all_cells = []
    for match in ALL_CELL_RE.finditer(output_file):
        #print(match)
        cell = [
            [match["xx"], match["xy"], match["xz"]],
            [match["yx"], match["yy"], match["yz"]],
            [match["zx"], match["zy"], match["zz"]]
        ]
        all_cells.append(cell)

    if all_cells:
        return np.array(all_cells, dtype=float)
    else:
        return None
