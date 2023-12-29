# from monty.io import zopen
import regex as re
import numpy as np
ENERGY_RE = re.compile(
    r"""(?x)
    \sE\s=\s+(?P<energy>[\s-]\d+\.\d+)
    """
)


def parse_md_ener(ener_file):
    print(f"Parsing Energies from {ener_file}")
    energies_list = np.loadtxt(ener_file, usecols=4, ndmin=1, dtype=np.float64)
    return energies_list


def parse_pos_xyz(posxyz_file):
    print(f"Parsing Structures from {posxyz_file}")
    fp = open(posxyz_file, "r")
    lines = fp.readlines()
    energies_list = []
    pos_list = []
    while len(lines) > 0:
        chemical_symbols = []
        positions = []
        natoms = int(lines.pop(0))
        match = ENERGY_RE.search(lines.pop(0))
        energies_list.append(match["energy"])
        for _ in range(natoms):
            line = lines.pop(0)
            symbol, x, y, z = line.split()[:4]
            symbol = symbol.lower().capitalize()
            chemical_symbols.append(symbol)
            positions.append([float(x), float(y), float(z)])
        pos_list.append(positions)
    energies_list = np.array(energies_list, dtype=np.float64)
    pos_list = np.array(pos_list, dtype=np.float64)
    return pos_list, energies_list, chemical_symbols


def parse_frc_xyz(frcxyz_file):
    print(f"Parsing Froces from {frcxyz_file}")
    fp = open(frcxyz_file, "r")
    lines = fp.readlines()
    force_list = []
    while len(lines) > 0:
        symbols = []
        positions = []
        natoms = int(lines.pop(0))
        lines.pop(0)
        for _ in range(natoms):
            line = lines.pop(0)
            symbol, x, y, z = line.split()[:4]
            symbol = symbol.lower().capitalize()
            symbols.append(symbol)
            positions.append([float(x), float(y), float(z)])
        force_list.append(positions)
    force_list = np.array(force_list, dtype=np.float64)
    return force_list

# NOTE: incomplete function, do not release!


def parse_pos_xyz_from_wannier(wannier_xyz_fiel):
    print(f"Parsing Structures from {wannier_xyz_fiel}")
    fp = open(wannier_xyz_fiel, "r")
    lines = fp.readlines()
    force_list = []
    while len(lines) > 0:
        symbols = []
        positions = []
        natoms = int(lines.pop(0))
        lines.pop(0)
        for _ in range(natoms):
            line = lines.pop(0)
            symbol, x, y, z = line.split()[:4]
            symbol = symbol.lower().capitalize()
            if symbol == 'X':
                continue
            symbols.append(symbol)
            positions.append([float(x), float(y), float(z)])
        force_list.append(positions)
    force_list = np.array(force_list, dtype=np.float64)
    return force_list


def parse_md_stress(stress_file):
    print(f"Parsing Stresses from {stress_file}")
    stresses_list = np.loadtxt(
        stress_file,
        usecols=(2, 3, 4, 5, 6, 7, 8, 9, 10),
        ndmin=2,
        dtype=np.float64
    )

    numb_frames = stresses_list.shape[0]

    return stresses_list.reshape(numb_frames, 3, 3)


def parse_md_cell(cell_file):
    print(f"Parsing Cells from {cell_file}")
    cells_list = np.loadtxt(
        cell_file,
        usecols=(2, 3, 4, 5, 6, 7, 8, 9, 10),
        ndmin=2,
        dtype=np.float64
    )
    numb_frames = cells_list.shape[0]

    return cells_list.reshape(numb_frames, 3, 3)
