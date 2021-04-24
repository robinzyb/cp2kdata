"""
this script put misc function here.
"""
from ase.geometry.analysis import Analysis
import numpy as np

# frequently used unit convertion
au2eV = 27.211386245988
au2A = 0.529177210903

def interpolate_spline(old_x, old_y, new_x):
    from scipy import interpolate
    f = interpolate.splrep(old_x, old_y, s=0)
    new_y = interpolate.splev(new_x, f)
    return new_x, new_y

def set_pbc(pos, cell):
    """set pbc for a list of Atoms object"""
    for single_pos in pos:
        single_pos.set_cell(cell)
        single_pos.set_pbc(True)

def get_rdf_list(pos, r, nbin, frames, elements):
    """
    pos: a list of atoms object
    r: the radial length
    nbin: the bin number in the radial range
    frames: how much pos number will you consider
    elements: the atom pair
    """
    tmp_info = Analysis(pos)
    # this wil get a rdf for every snapshot
    tmp_rdf_list = tmp_info.get_rdf(r, nbin, imageIdx=slice(0, frames, 1), elements=elements)
    return tmp_rdf_list

def get_rdf(pos, r, nbin, frames, elements):
    """

    """
    tmp_rdf_list = get_rdf_list(pos, r, nbin, frames, elements)
    tot_gr = np.zeros(nbin)
    for s_gr in tmp_rdf_list:
        tot_gr += s_gr/frames
    return tot_gr

def printtbox(arg):
    """
    This function is a print decorated with a few characters so that the
    print function present a characteristic string. Useful for postprocess.
    """
    print("--> CP2KDATA: {0}".format(arg))

def file_content(file, num):
    # read a specific line of file or return the block
    # file: enter file name
    # num: a integer -> return specific line content
    #      a tuple (num1, num2) -> return the line content
    #                              between num1 and num2-1
    #      a tuple (num1, ) -> return the line content from
    #                          num1, to the end of file
    if isinstance(num, int):
        with open(file) as f:
            for _idx, line in enumerate(f):
                if _idx == num:
                    return line
    elif isinstance(num, tuple):
        content = ""
        if len(num) == 2:
            with open(file) as f:
                for _idx, line in enumerate(f):
                    if (_idx >= num[0]) and (_idx < num[1]):
                        content += line
                    elif _idx >= num[1]:
                        break
                    else:
                        continue
            return content
        elif len(num) == 1:
            with open(file) as f:
                for _idx, line in enumerate(f):
                    if (_idx >= num[0]) :
                        content += line
            return content
        else:
            raise ValueError("The length of range is wrong!")
