from dpdata.unit import EnergyConversion, LengthConversion, ForceConversion, PressureConversion
from dpdata.format import Format
from . import Cp2kOutput
from .block_parser.converge import parse_e_f_converge
import numpy as np
from cp2kdata.block_parser.md_xyz import parse_pos_xyz_from_wannier
import os

AU_TO_EV = EnergyConversion("hartree", "eV").value()
AU_TO_ANG = LengthConversion("bohr", "angstrom").value()
EV_ANG_m3_TO_GPa = PressureConversion("eV/angstrom^3", "GPa").value()


WRAPPER = "--- You are parsing data using package Cp2kData ---"
VIRIAL_WRN = (
    "Virial Parsing using cp2kdata as plug in for dpdata\n"
    "was not multiplied by volume before cp2kdata v0.6.4\n"
    "please check the cp2kdata version and the virial.npy\n"
    )


@Format.register("cp2k/output")
@Format.register("cp2kdata/e_f")
class CP2KEnergyForceFormat(Format):
    def from_labeled_system(self, file_name, **kwargs):

        # -- Set Basic Parameters --
        true_symbols = kwargs.get('true_symbols', False)

        # -- start parsing --
        print(WRAPPER)
        converge_info = parse_e_f_converge(file_name)
        if not converge_info.converge:
            data = {
                'atom_names': [],
                'atom_numbs': [],
                'atom_types': [],
                'energies': [],
                'cells': [],
                'coords': [],
                'forces': []
            }
            return data

        cp2k_e_f = Cp2kOutput(file_name)

        chemical_symbols = get_chemical_symbols_from_cp2kdata(
            cp2koutput=cp2k_e_f,
            true_symbols=true_symbols
        )

        # -- data dict collects information, and return to dpdata --

        data = {}
        data['atom_names'], data['atom_numbs'], data["atom_types"] = get_uniq_atom_names_and_types(
            chemical_symbols=chemical_symbols)
        # atom_numbs not total num of atoms!
        data['energies'] = cp2k_e_f.energies_list * AU_TO_EV
        data['cells'] = cp2k_e_f.get_init_cell()[np.newaxis, :, :]
        data['coords'] = cp2k_e_f.init_atomic_coordinates[np.newaxis, :, :]
        data['forces'] = cp2k_e_f.atomic_forces_list * AU_TO_EV/AU_TO_ANG
        if cp2k_e_f.has_stress():
            # note that virial = stress * volume
            print(VIRIAL_WRN)
            volume = np.linalg.det(data['cells'][0])
            data['virials'] = cp2k_e_f.stress_tensor_list*volume/EV_ANG_m3_TO_GPa

        print(WRAPPER)
        return data


@Format.register("cp2k/aimd_output")
@Format.register("cp2kdata/md")
class CP2KMDFormat(Format):
    def from_labeled_system(self, file_name, **kwargs):

        # -- Set Basic Parameters --
        path_prefix = file_name  # in cp2k md, file_name is directory name.
        true_symbols = kwargs.get('true_symbols', False)
        cells = kwargs.get('cells', None)
        cp2k_output_name = kwargs.get('cp2k_output_name', None)

        # -- start parsing --
        print(WRAPPER)

        cp2kmd = Cp2kOutput(output_file=cp2k_output_name,
                            run_type="MD", path_prefix=path_prefix)

        num_frames = cp2kmd.get_num_frames()

        chemical_symbols = get_chemical_symbols_from_cp2kdata(
            cp2koutput=cp2kmd,
            true_symbols=true_symbols
        )

        if cells is None:
            if cp2kmd.filename:
                # cells = cp2kmd.get_init_cell()
                # cells = cells[np.newaxis, :, :]
                # cells = np.repeat(cells, repeats=num_frames, axis=0)
                cells = cp2kmd.get_all_cells()
            else:
                print("No cell information, please check if your inputs are correct.")
        elif isinstance(cells, np.ndarray):
            if cells.shape == (3, 3):
                cells = cells[np.newaxis, :, :]
                cells = np.repeat(cells, repeats=num_frames, axis=0)
            elif cells.shape == (num_frames, 3, 3):
                pass
            else:
                print(
                    "Illegal Cell Information, cells shape should be (num_frames, 3, 3) or (3, 3)")
        else:
            print(
                "Illegal Cell Information, cp2kdata accepts np.ndarray as cells information")

        # -- data dict collects information, and return to dpdata --
        data = {}
        data['atom_names'], data['atom_numbs'], data["atom_types"] = get_uniq_atom_names_and_types(
            chemical_symbols=chemical_symbols)
        # atom_numbs not total num of atoms!
        data['energies'] = cp2kmd.energies_list * AU_TO_EV
        data['cells'] = cells
        data['coords'] = cp2kmd.atomic_frames_list
        data['forces'] = cp2kmd.atomic_forces_list * AU_TO_EV/AU_TO_ANG
        if cp2kmd.has_stress():
            # note that virial = stress * volume
            print(VIRIAL_WRN)
            # the shape of cells should be (num_frames, 3, 3)
            # the np.linalg.det() function can handle this and return (num_frames,)
            volumes = np.linalg.det(data['cells'])
            volumes = volumes[:, np.newaxis, np.newaxis]
            data['virials'] = cp2kmd.stress_tensor_list*volumes/EV_ANG_m3_TO_GPa

        print(WRAPPER)
        return data


def get_chemical_symbols_from_cp2kdata(cp2koutput, true_symbols):
    if cp2koutput.atomic_kind is None:
        print("Missing the atomic kind informations, atom names are true chemical symbols.")
        chemical_symbols = cp2koutput.get_chemical_symbols()
    elif true_symbols:
        print("You have manually true_symbols=True, atom names are true chemical symbols.")
        chemical_symbols = cp2koutput.get_chemical_symbols()
    else:
        print("Atom names are fake chemical symbols as you set in cp2k input.")
        chemical_symbols = cp2koutput.get_chemical_symbols_fake()
    chemical_symbols = np.array(chemical_symbols)
    return chemical_symbols


def get_uniq_atom_names_and_types(chemical_symbols):
    _, symbol_idx = np.unique(chemical_symbols, return_index=True)
    atom_types = []
    atom_numbs = []
    # -- preserve the atom_name order --
    atom_names = chemical_symbols[np.sort(symbol_idx)]
    for jj in chemical_symbols:
        for idx, ii in enumerate(atom_names):
            if (jj == ii):
                atom_types.append(idx)
    for idx in range(len(atom_names)):
        atom_numbs.append(atom_types.count(idx))

    atom_types = np.array(atom_types)

    return list(atom_names), atom_numbs, atom_types

# NOTE: incomplete function, do not release!


@Format.register("cp2kdata/md_wannier")
class CP2KMDWannierFormat(Format):
    def from_labeled_system(self, file_name, **kwargs):

        # -- Set Basic Parameters --
        path_prefix = file_name  # in cp2k md, file_name is directory name.
        true_symbols = kwargs.get('true_symbols', False)
        cells = kwargs.get('cells', None)
        cp2k_output_name = kwargs.get('cp2k_output_name', None)

        # -- start parsing --
        print(WRAPPER)

        cp2kmd = Cp2kOutput(output_file=cp2k_output_name,
                            run_type="MD", path_prefix=path_prefix)

        num_frames = cp2kmd.get_num_frames()

        chemical_symbols = get_chemical_symbols_from_cp2kdata(
            cp2koutput=cp2kmd,
            true_symbols=true_symbols
        )

        if cells is None:
            if cp2kmd.filename:
                # cells = cp2kmd.get_init_cell()
                # cells = cells[np.newaxis, :, :]
                # cells = np.repeat(cells, repeats=num_frames, axis=0)
                cells = cp2kmd.get_all_cells()
            else:
                print("No cell information, please check if your inputs are correct.")
        elif isinstance(cells, np.ndarray):
            if cells.shape == (3, 3):
                cells = cells[np.newaxis, :, :]
                cells = np.repeat(cells, repeats=num_frames, axis=0)
            elif cells.shape == (num_frames, 3, 3):
                pass
            else:
                print(
                    "Illegal Cell Information, cells shape should be (num_frames, 3, 3) or (3, 3)")
        else:
            print(
                "Illegal Cell Information, cp2kdata accepts np.ndarray as cells information")

        # -- data dict collects information, and return to dpdata --
        data = {}
        data['atom_names'], data['atom_numbs'], data["atom_types"] = get_uniq_atom_names_and_types(
            chemical_symbols=chemical_symbols)
        # atom_numbs not total num of atoms!
        data['energies'] = cp2kmd.energies_list * AU_TO_EV
        data['cells'] = cells

        # get wannier centers from wannier xyz file

        cp2k_wannier_file = kwargs.get('cp2k_wannier_file', None)
        if cp2k_wannier_file:
            print("This is wannier center parser")
            print("Position parsed from pos files are not used.")
            cp2k_wannier_file = os.path.join(path_prefix, cp2k_wannier_file)
            data['coords'] = parse_pos_xyz_from_wannier(cp2k_wannier_file)
        else:
            raise ValueError("Please specify the cp2k wannier file name!")

        data['forces'] = cp2kmd.atomic_forces_list * AU_TO_EV/AU_TO_ANG
        if cp2kmd.has_stress():
            data['virials'] = cp2kmd.stress_tensor_list/EV_ANG_m3_TO_GPa
        # print(len(data['cells']), len(data['coords']), len(data['energies']))
        print(WRAPPER)
        return data
