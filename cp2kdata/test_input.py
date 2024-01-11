# Generate Cp2k Test Inputs
from .utils import create_path
from pycp2k import CP2K
import os
import shutil
import copy
import glob
import numpy as np


def remove_section(sec_obj):
    """remove pycp2k section to prevent it print in cp2k input file

    Args:
        sec_obj ([type]): Pycp2k section object
    """
    # just set the keywords and subsection keywords to None is ok
    for attname, realname in sec_obj._keywords.items():
        value = sec_obj.__dict__[attname]
        if value is not None:
            sec_obj.__dict__[attname] = None

    for attname, realname in sec_obj._subsections.items():
        value = sec_obj.__dict__[attname]
        remove_section(value)


def copy_file_list(file_list, target_dir):
    for file in file_list:
        src = file
        dst = os.path.join(target_dir, file)
        if os.path.isdir(src):
            shutil.copytree(src, dst, symlinks=True)
        elif os.path.isfile(src):
            shutil.copy2(src, dst)


def get_CP2K(cp2k_input_file):
    inp = CP2K()
    inp.parse(cp2k_input_file)
    return inp


def get_batch_inp(
    cp2k: CP2K,
    stc_list: list
):

    FORCE_EVAL = cp2k.CP2K_INPUT.FORCE_EVAL_list[0]
    SUBSYS = FORCE_EVAL.SUBSYS
    remove_section(SUBSYS.CELL)
    remove_section(SUBSYS.COORD)

    cp2k_list = []
    for stc in stc_list:
        new_cp2k = copy.deepcopy(cp2k)
        FORCE_EVAL = new_cp2k.CP2K_INPUT.FORCE_EVAL_list[0]
        SUBSYS = FORCE_EVAL.SUBSYS
        new_cp2k.create_cell(SUBSYS, stc)
        new_cp2k.create_coord(SUBSYS, stc)
        cp2k_list.append(new_cp2k)

    return cp2k_list


def batch_sub(
    sub_cmd: str = "bsub<cp2k",
    target_dir: str = ".",
    sub_dir_name_list: list = None
):
    target_dir = os.path.abspath(target_dir)
    if sub_dir_name_list is None:
        sub_dir_list = glob.glob(os.path.join(target_dir, "*"))
    else:
        sub_dir_list = [os.path.join(target_dir, sub_dir_name)
                        for sub_dir_name in sub_dir_name_list]

    for sub_dir in sub_dir_list:
        os.chdir(sub_dir)
        os.system(sub_cmd)


def write_batch_inp(
    cp2k_list: list,
    target_dir: str = ".",
    dir_name: str = "calc",
    suffix_list: list = None,
    other_file_list: list = []
):
    if suffix_list is None:
        suffix_list = [str(i) for i in range(len(cp2k_list))]
    sub_dir_name_list = [dir_name+"_"+suffix for suffix in suffix_list]

    for idx, cp2k in enumerate(cp2k_list):
        calc_sub_dir = os.path.join(
            target_dir, f"{idx:03d}.{sub_dir_name_list[idx]}")
        create_path(calc_sub_dir)
        copy_file_list(file_list=other_file_list, target_dir=calc_sub_dir)

        input_path = os.path.join(calc_sub_dir, "input.inp")

        cp2k.write_input_file(input_path)


def write_cutoff_test_inp(
    cp2k: CP2K,
    target_dir: str = ".",
    cutoff_range: tuple = (300, 601, 50),
    other_file_list: list = [],
    scf_converge: bool = False

):
    """_summary_

    _extended_summary_

    Args:
        cp2k (_type_): _description_
        target_dir (str, optional): _description_. Defaults to ".".
        cutoff_range (tuple, optional): _description_. Defaults to (300, 601, 50).
        other_file_list (list, optional): _description_. Defaults to [].
    """
    FORCE_EVAL = cp2k.CP2K_INPUT.FORCE_EVAL_list[0]

    FORCE_EVAL.Stress_tensor = "ANALYTICAL"

    FORCE_EVAL.PRINT.STRESS_TENSOR.Section_parameters = "ON"
    FORCE_EVAL.PRINT.FORCES.Section_parameters = "ON"

    DFT = FORCE_EVAL.DFT
    # DFT.MGRID.Rel_cutoff = rel_cutoff
    DFT.MGRID.Ngrids = 4

    if scf_converge:
        pass
    else:
        SCF = DFT.SCF
        SCF.Max_scf = 1
        remove_section(SCF.OUTER_SCF)
    # SCF.Scf_guess = "RESTART"

    GLOBAL = cp2k.CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = "ENERGY_FORCE"

    # cutoff_test_dir = os.path.join(target_dir, "cutoff_test")
    # create_path(cutoff_test_dir)
    for idx, param in enumerate(range(*cutoff_range)):

        DFT.MGRID.Cutoff = param

        cutoff_test_sub_dir = os.path.join(target_dir, f"cutoff_{param:04d}")
        create_path(cutoff_test_sub_dir)

        copy_file_list(file_list=other_file_list,
                       target_dir=cutoff_test_sub_dir)

        input_path = os.path.join(cutoff_test_sub_dir, "input.inp")
        cp2k.write_input_file(input_path)


basis_molopt_test_suit = {
    "H": ["SZV-MOLOPT-GTH", "DZVP-MOLOPT-GTH", "TZVP-MOLOPT-GTH", "TZV2P-MOLOPT-GTH", "TZV2PX-MOLOPT-GTH"],
    "O": ["SZV-MOLOPT-GTH", "DZVP-MOLOPT-GTH", "TZVP-MOLOPT-GTH", "TZV2P-MOLOPT-GTH", "TZV2PX-MOLOPT-GTH"],
    "Ti": ["DZVP-MOLOPT-PBE-GTH-q12", "TZVP-MOLOPT-PBE-GTH-q12", "TZV2P-MOLOPT-PBE-GTH-q12"],
    "Fe": ["DZVP-MOLOPT-PBE-GTH-q16", "TZVP-MOLOPT-PBE-GTH-q16", "TZV2P-MOLOPT-PBE-GTH-q16"],
    "Co": ["DZVP-MOLOPT-PBE-GTH-q17", "TZVP-MOLOPT-PBE-GTH-q17", "TZV2P-MOLOPT-PBE-GTH-q17"]
}

basis_molopt_sr_test_suit = {
    "H": ["SZV-MOLOPT-SR-GTH", "DZVP-MOLOPT-SR-GTH"],
    "O": ["SZV-MOLOPT-SR-GTH", "DZVP-MOLOPT-SR-GTH"],
    "Ti": ["SZV-MOLOPT-SR-GTH", "DZVP-MOLOPT-SR-GTH", "TZVP-MOLOPT-SR-GTH", "TZV2P-MOLOPT-SR-GTH"],
    "Fe": ["SZV-MOLOPT-SR-GTH", "DZVP-MOLOPT-SR-GTH", "TZVP-MOLOPT-SR-GTH", "TZV2P-MOLOPT-SR-GTH"],
    "Co": ["SZV-MOLOPT-SR-GTH", "DZVP-MOLOPT-SR-GTH", "TZVP-MOLOPT-SR-GTH", "TZV2P-MOLOPT-SR-GTH"],
}


def write_basis_test_inp(
    cp2k: CP2K,
    target_dir: str = ".",
    test_element: str = "O",
    short_range: bool = True,
    other_file_list: list = []
):
    FORCE_EVAL = cp2k.CP2K_INPUT.FORCE_EVAL_list[0]

    FORCE_EVAL.Stress_tensor = "ANALYTICAL"
    FORCE_EVAL.PRINT.STRESS_TENSOR.Section_parameters = "ON"
    FORCE_EVAL.PRINT.FORCES.Section_parameters = "ON"
    DFT = FORCE_EVAL.DFT
    # DFT.MGRID.Rel_cutoff = rel_cutoff
    DFT.MGRID.Ngrids = 4

    DFT.Basis_set_file_name = \
        [
            "BASIS_MOLOPT",
            "BASIS_MOLOPT_AcPP1",
            "BASIS_MOLOPT_LnPP1",
            "BASIS_MOLOPT_UCL",
            "BASIS_MOLOPT_UZH"
        ]

    GLOBAL = cp2k.CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = "ENERGY_FORCE"

    if short_range:
        basis_set_suit = basis_molopt_sr_test_suit
    else:
        basis_set_suit = basis_molopt_test_suit

    for basis_set in basis_set_suit[test_element]:

        for KIND in FORCE_EVAL.SUBSYS.KIND_list:
            if (KIND.Element is None) and (KIND.Section_parameters == test_element):
                KIND.Basis_set = [basis_set]
            elif (KIND.Element == test_element):
                KIND.Basis_set = [basis_set]
            else:
                pass
        basis_test_sub_dir = os.path.join(target_dir, f"basis_{basis_set}")
        create_path(basis_test_sub_dir)
        copy_file_list(file_list=other_file_list,
                       target_dir=basis_test_sub_dir)
        input_path = os.path.join(basis_test_sub_dir, "input.inp")
        cp2k.write_input_file(input_path)


def write_hubbard_U_test_inp(
    cp2k: CP2K,
    target_dir: str = ".",
    u_range: tuple = (0, 8, 1),
    test_element: str = "O",
    test_orbital: str = "p",
    other_file_list: list = []
):
    FORCE_EVAL = cp2k.CP2K_INPUT.FORCE_EVAL_list[0]

    FORCE_EVAL.Stress_tensor = "ANALYTICAL"
    FORCE_EVAL.PRINT.STRESS_TENSOR.Section_parameters = "ON"
    FORCE_EVAL.PRINT.FORCES.Section_parameters = "ON"
    DFT = FORCE_EVAL.DFT

    DFT.MGRID.Ngrids = 4
    DFT.Plus_u_method = "mulliken"

    GLOBAL = cp2k.CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = "CELL_OPT"

    MOTION = cp2k.CP2K_INPUT.MOTION
    MOTION.CELL_OPT.Optimizer = "LBFGS"
    MOTION.CELL_OPT.Keep_angles = True

    ang_quant_num_dict = {
        "s": 0,
        "p": 1,
        "d": 2,
        "f": 3
    }

    for U in np.arange(*u_range):
        for KIND in FORCE_EVAL.SUBSYS.KIND_list:
            if (KIND.Element is None) and (KIND.Section_parameters == test_element):
                KIND.DFT_PLUS_U.L = ang_quant_num_dict[test_orbital]
                KIND.DFT_PLUS_U.U_minus_j = f"[eV] {U}"
            elif (KIND.Element == test_element):
                KIND.DFT_PLUS_U.L = ang_quant_num_dict[test_orbital]
                KIND.DFT_PLUS_U.U_minus_j = f"[eV] {U}"
            else:
                pass

        U_test_sub_dir = os.path.join(target_dir, f"U_{U:04.2f}")
        create_path(U_test_sub_dir)
        copy_file_list(file_list=other_file_list, target_dir=U_test_sub_dir)
        input_path = os.path.join(U_test_sub_dir, "input.inp")
        cp2k.write_input_file(input_path)
