from typing_extensions import clear_overloads
from dpdata.format import Format
from . import Cp2kOutput
import numpy as np

@Format.register("cp2kdata/md")
class CP2KMDFormat(Format):
    def from_labeled_system(self, path_prefix=".", cells=None, **kwargs):
        
        # todo: parse cell from log, or manually set
        # "cells = something"
        cp2kmd = Cp2kOutput(run_type="MD", path_prefix=path_prefix)

        if cp2kmd.atomic_kind is None:
            chemical_symbols = cp2kmd.get_chemical_symbols()
        else: 
            chemical_symbols = cp2kmd.get_chemical_symbols_fake()

        data = {}
        data['atom_names'], data["atom_types"] = get_uniq_atom_names_and_types(chemical_symbols=chemical_symbols)
        data['atom_numbs'] = np.full(cp2kmd.get_num_frames(), cp2kmd.get_num_atoms())
        data['energies'] = cp2kmd.energies_list
        #modify here
        data['cells'] = cells
        data['coords'] = cp2kmd.atomic_frames_list
        data['forces'] = cp2kmd.atomic_forces_list
        if cp2kmd.stress_tensor_list.any():
            data['virials'] = cp2kmd.stress_tensor_list

        return data

def get_uniq_atom_names_and_types(chemical_symbols):
    _, symbol_idx = np.unique(chemical_symbols, return_index=True)
    atom_types = []
    atom_numbs = []
    #preserve the atom_name order
    atom_names = chemical_symbols[np.sort(symbol_idx)]
    for jj in chemical_symbols:
        for idx, ii in enumerate(atom_names):
            if (jj == ii) :
                atom_types.append(idx)
    for idx in range(len(atom_names)):
        atom_numbs.append(atom_types.count(idx))

    atom_types = np.array(atom_types)

    return list(atom_names), atom_types