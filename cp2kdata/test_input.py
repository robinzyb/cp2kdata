from .utils import create_path
import os


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


def write_eps_pgf_orb_test_inp(
    pycp2k_inobj, 
    target_dir: str=".",
    cutoff_range: tuple=(300, 601, 50)):
    """_summary_

    _extended_summary_

    Args:
        pycp2k_inobj (_type_): _description_
        cutoff_range (tuple, optional): _description_. Defaults to (300, 601, 50).
    """  
    FORCE_EVAL = pycp2k_inobj.CP2K_INPUT.FORCE_EVAL_list[0]
    DFT = FORCE_EVAL.DFT
    DFT.MGRID.REL_CUTOFF = 60
    DFT.MGRID.NGRIDS = 4

    SCF = DFT.SCF
    SCF.Max_scf = 1
    #SCF.Scf_guess = "RESTART"

    remove_section(SCF.OUTER_SCF)

    GLOBAL = pycp2k_inobj.CP2K_INPUT.GLOBAL
    GLOBAL.Run_type = "ENERGY_FORCE"

    create_path(os.path.join(target_dir, "cutoff_test"))
    for param in cutoff_range:
        DFT.MGRID.CUTOFF = param
        create_path(f"cutoff_test/param_{param}")
        input_path = os.path.join(
            target_dir,
            "cutoff_test",
            f"param_{param}",
            "input.inp"
            )
        pycp2k_inobj.write_input_file(input_path)