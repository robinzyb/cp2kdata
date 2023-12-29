import numpy as np


def parse_vertical_gap(mix_ener_file, r_col=3, p_col=4):
    r_ener = np.loadtxt(mix_ener_file, usecols=r_col)
    p_ener = np.loadtxt(mix_ener_file, usecols=p_col)
    v_gap = p_ener - r_ener
    return v_gap
