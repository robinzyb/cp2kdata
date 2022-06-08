from .utils import create_path
import os
import shutil


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



def write_cutoff_test_inp(
    pycp2k_inobj, 
    target_dir: str=".",
    cutoff_range: tuple=(300, 601, 50),
    rel_cutoff: int=60,
    other_file_list: list=[],
    scf_converge: bool = False
    
    ):
    """_summary_

    _extended_summary_

    Args:
        pycp2k_inobj (_type_): _description_
        target_dir (str, optional): _description_. Defaults to ".".
        cutoff_range (tuple, optional): _description_. Defaults to (300, 601, 50).
        other_file_list (list, optional): _description_. Defaults to [].
    """    
    FORCE_EVAL = pycp2k_inobj.CP2K_INPUT.FORCE_EVAL_list[0]

    FORCE_EVAL.Stress_tensor = "ANALYTICAL"

    FORCE_EVAL.PRINT.STRESS_TENSOR.Section_parameters = "ON"
    FORCE_EVAL.PRINT.FORCES.Section_parameters  = "ON"

    DFT = FORCE_EVAL.DFT
    DFT.MGRID.Rel_cutoff = rel_cutoff
    DFT.MGRID.Ngrids = 4

    if scf_converge:
        pass
    else:
        SCF = DFT.SCF
        SCF.Max_scf = 1
        remove_section(SCF.OUTER_SCF)
    #SCF.Scf_guess = "RESTART"


    GLOBAL = pycp2k_inobj.CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = "ENERGY_FORCE"

    cutoff_test_dir = os.path.join(target_dir, "cutoff_test")
    create_path(cutoff_test_dir)
    for idx, param in enumerate(range(*cutoff_range)):

        DFT.MGRID.Cutoff = param

        cutoff_test_sub_dir = os.path.join(cutoff_test_dir, f"{idx:03d}.param_{param}")
        create_path(cutoff_test_sub_dir)
        
        copy_file_list(file_list=other_file_list, target_dir=cutoff_test_sub_dir)

        input_path = os.path.join(cutoff_test_sub_dir, "input.inp")
        pycp2k_inobj.write_input_file(input_path)




    