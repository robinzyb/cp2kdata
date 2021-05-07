from scipy.ndimage import gaussian_filter1d
from toolkit.utils import au2eV
from toolkit.cp2k.cube import interpolate_spline
import numpy as np

def read_dos_element(file):
    with open(file) as f:
        first_line = f.readline()
        element = first_line.split()[6]
    return element

def read_dos_fermi(file):
    with open(file) as f:
        first_line = f.readline()
        fermi_idx = first_line.split().index("E(Fermi)")
        fermi = first_line.split()[fermi_idx+2]
        fermi = float(fermi)*au2eV
    return fermi

def read_dos_energies(file):
    energies = np.loadtxt(file, usecols=1)
    energies = energies * au2eV
    return energies

def get_raw_dos(energies, fermi, weights, steplen=0.1):
    bins = int((energies[-1]-energies[0])/steplen)
    dos, ener = np.histogram(energies, bins, weights=weights, range=(energies[0], energies[-1]))
    dos = dos/steplen
    ener = ener[:-1] - fermi + 0.5*steplen
    return dos, ener

def dos_smth(dos, sigma=0.2):
    #smooth the dos data
    smth_dos = gaussian_filter1d(dos, sigma)
    return smth_dos

def get_dos(file, dos_type="total", ldos=False, smooth=True):
    # get the dos from cp2k pdos file
    # dos_type: total, s, p, d
    # return information, dos, ener
    info = {}
    info['element'] = read_dos_element(file)
    info['fermi'] = read_dos_fermi(file)
    # read energy
    energies = read_dos_energies(file)
    # decide the weight from dos_type
    if ldos :
        if dos_type == "total":
            weights = np.loadtxt(file, usecols = (3, 4, 5)).sum(axis=1)
        elif dos_type == "s":
            weights = np.loadtxt(file, usecols = 3)
        elif dos_type == "p":
            weights = np.loadtxt(file, usecols = 4)
        elif dos_type == "d":
            weights = np.loadtxt(file, usecols = 5)
        elif dos_type == "f":
            weights = np.loadtxt(file, usecols = 6)
    else:
        if dos_type == "total":
            tmp_len = len(np.loadtxt(file, usecols = 2))
            weights = np.ones(tmp_len)
        elif dos_type == "s":
            weights = np.loadtxt(file, usecols = 3)
        elif dos_type == "p":
            weights = np.loadtxt(file, usecols = (4,5,6)).sum(axis=1)
        elif dos_type == "d":
            weights = np.loadtxt(file, usecols = (7,8,9,10,11)).sum(axis=1)
        elif dos_type == "f":
            weights = np.loadtxt(file, usecols = (12,13,14,15,16,17,18)).sum(axis=1)
        else:
            raise NameError("dos type does not exist!")
    # make dos by histogram
    dos, ener = get_raw_dos(energies, info['fermi'], weights)
    # smooth
    if smooth:
        new_points = np.linspace(-10, 5, 500)
        new_points, new_vals = interpolate_spline(ener, dos, new_points)
    return new_vals, new_points, info

class pdos():
    def __init__(self, file_name, fermi, element):
        self.element = read_dos_element(file_name)
        self.fermi = read_dos_fermi(file_name)
