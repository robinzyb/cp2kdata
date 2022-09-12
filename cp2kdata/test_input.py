from .utils import create_path
from pycp2k import CP2K
import os
import shutil
import copy
import glob


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
    sub_cmd: str="bsub<cp2k", 
    target_dir: str = ".",
    sub_dir_name_list: list=None
    ):
    target_dir = os.path.abspath(target_dir)
    if sub_dir_name_list is None:
        sub_dir_list = glob.glob(os.path.join(target_dir, "*"))
    else:
        sub_dir_list = [ os.path.join(target_dir, sub_dir_name) for sub_dir_name in sub_dir_name_list]

    for sub_dir in sub_dir_list:
        os.chdir(sub_dir)
        os.system(sub_cmd)


def write_batch_inp(
    cp2k_list: list,
    target_dir: str=".",
    dir_name: str= "calc",
    suffix_list: list=None,
    other_file_list: list=[]
    ):
    if suffix_list is None:
        suffix_list = [ str(i) for i in range(len(cp2k_list)) ]
    sub_dir_name_list = [ dir_name+"_"+suffix  for suffix in suffix_list ]

    for idx, cp2k in enumerate(cp2k_list):
        calc_sub_dir = os.path.join(target_dir, f"{idx:03d}.{sub_dir_name_list[idx]}")
        create_path(calc_sub_dir)
        copy_file_list(file_list=other_file_list, target_dir=calc_sub_dir)

        input_path = os.path.join(calc_sub_dir, "input.inp")
        
        cp2k.write_input_file(input_path)

        


def write_cutoff_test_inp(
    cp2k: CP2K, 
    target_dir: str=".",
    cutoff_range: tuple=(300, 601, 50),
    other_file_list: list=[],
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
    FORCE_EVAL.PRINT.FORCES.Section_parameters  = "ON"

    DFT = FORCE_EVAL.DFT
    #DFT.MGRID.Rel_cutoff = rel_cutoff
    DFT.MGRID.Ngrids = 4

    if scf_converge:
        pass
    else:
        SCF = DFT.SCF
        SCF.Max_scf = 1
        remove_section(SCF.OUTER_SCF)
    #SCF.Scf_guess = "RESTART"


    GLOBAL = cp2k.CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = "ENERGY_FORCE"

    # cutoff_test_dir = os.path.join(target_dir, "cutoff_test")
    # create_path(cutoff_test_dir)
    for idx, param in enumerate(range(*cutoff_range)):

        DFT.MGRID.Cutoff = param

        cutoff_test_sub_dir = os.path.join(target_dir, f"cutoff_{param:04d}")
        create_path(cutoff_test_sub_dir)
        
        copy_file_list(file_list=other_file_list, target_dir=cutoff_test_sub_dir)

        input_path = os.path.join(cutoff_test_sub_dir, "input.inp")
        cp2k.write_input_file(input_path)




    