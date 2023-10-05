import regex as re
import numpy as np
from ase.geometry.cell import cellpar_to_cell

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
    

ALL_MD_CELL_RE = re.compile(
    r"""
    #parse cell lengths
    \sMD\|\sCell\slengths\s\[ang\]\s{9}
    \s{2}(?P<a>\d\.\d{8}E(\+|\-)\d{2})
    \s{2}(?P<b>\d\.\d{8}E(\+|\-)\d{2})
    \s{2}(?P<c>\d\.\d{8}E(\+|\-)\d{2})
    \n
    #skip two lines
    (.{80}\n){2}
    #parse angles
    \sMD\|\sCell\sangles\s\[deg\]\s{10} 
    \s{2}(?P<alpha>\d\.\d{8}E(\+|\-)\d{2})
    \s{2}(?P<beta>\d\.\d{8}E(\+|\-)\d{2})
    \s{2}(?P<gamma>\d\.\d{8}E(\+|\-)\d{2})
    """,
    re.VERBOSE
)

def parse_all_md_cells(output_file):
    # notice that the cell of step 0 is not included
    all_md_cells = []
    for match in ALL_MD_CELL_RE.finditer(output_file):
        #print(match)
        cell = [match["a"], match["b"], match["c"],
             match["alpha"], match["beta"], match["gamma"]]
        cell = np.array(cell, dtype=float)
        cell = cellpar_to_cell(cell)
        all_md_cells.append(cell)

    if all_md_cells:
        return np.array(all_md_cells, dtype=float)
    else:
        return None