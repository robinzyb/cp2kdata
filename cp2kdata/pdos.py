from .utils import au2eV
from scipy.ndimage import gaussian_filter1d
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import glob

class Pdos():
    def __init__(self, file_name):
        self.file = file_name
        self.element = self.read_dos_element()
        self.fermi = self.read_dos_fermi()
        self.energies = self.read_dos_energies()
        self.project_name, self.spin, self.timestep, self.ldos = pdos_name_parser(self.file)

    def read_dos_element(self):
        with open(self.file) as f:
            first_line = f.readline()
            element = first_line.split()[6]
        return element

    def read_dos_fermi(self):
        # this is fermi energy not fermi level!
        # fermi energy is same as HOMO energy
        with open(self.file) as f:
            first_line = f.readline()
            fermi_idx = first_line.split().index("E(Fermi)")
            fermi = first_line.split()[fermi_idx+2]
            fermi = float(fermi)*au2eV
        return fermi

    def read_dos_energies(self):
        energies = np.loadtxt(self.file, usecols=1)
        energies = energies * au2eV
        return energies

    def get_raw_dos(self, dos_type="total"):

        file = self.file
        energies = self.energies
        fermi = self.fermi
        steplen = 0.1
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

        bins = int((energies[-1]-energies[0])/steplen)
        dos, ener = np.histogram(energies, bins,
                weights=weights, range=(energies[0], energies[-1]))
        dos = dos/steplen
        ener = ener[:-1] - fermi + 0.5*steplen
        self.dos = dos
        self.ener = ener
        return dos, ener

    def get_dos(self, sigma=1, dos_type="total"):
        # smooth the dos data
        dos, ener = self.get_raw_dos(dos_type=dos_type)
        smth_dos = gaussian_filter1d(dos, sigma)
        self.smth_dos = smth_dos

        return smth_dos, ener


def pdos_name_parser(filename):
    # used to parse pdos filename
    filename = os.path.basename(filename)

    project_name, tmp_1, tmp_2 = filename.split(sep="-")
    try:
        spin, species = tmp_1.split(sep="_")
    except:
        species = tmp_1
        spin = None
    # check spin
    spin_list = ["ALPHA", "BETA"]
    if spin in spin_list:
        pass
    elif spin == None:
        pass
    else:
        print("file name is not standard, spin is set to None")
        spin = None
    # check ldos
    if "k" in species:
        ldos = False
    elif "list" in species:
        ldos = True
    # remove suffix/extension
    tmp_3, _ = tmp_2.split(sep=".")
    # get step number
    _, step = tmp_3.split(sep="_")
    return project_name, spin, float(step), ldos

def typical_orbital(element):
    # input the element and return typical orbital in dos
    # for example d for Ti, s for H, p for O
    s_orb_list = ["H", "Li", "Na", "K", "Rb", "Cs", "Be", "Mg", "Ca", "Sr", "Ba"]
    p_orb_list = [
            "O", "S", "Se", "Te", "N", "P", "As", "Sb", "Bi",
            "C", "Si", "Ge", "Sn", "Pb",
            "B", "Al", "Ga", "In", "Tl",
            "F", "Cl", "Br", "I"
            ]
    d_orb_list = [
            "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
            "Y", "Zr", "Nb", "Mo", "Te", "Ru", "Rh", "Pd", "Ag", "Cd",
            "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"
            ]
    f_orb_list = [
            "La", "Ce", "Pr"
            ]
    if element in s_orb_list:
        return "s"
    elif element in p_orb_list:
        return "p"
    elif element in d_orb_list:
        return "d"
    elif element in f_orb_list:
        return "f"
    else:
        print("Typical orbital for this element is not known yet")
        return None

def quick_plot_uks(pdos_dir):
    # parameter setting
    fontsize = 15
    lw = 1.5

    # find pdos files
    pdos_files = glob.glob(os.path.join(pdos_dir, "*pdos"))
    pdos_files.sort()

    #
    alpha_dos = []
    beta_dos = []
    for i in pdos_files:
        tmp = Pdos(i)
        if tmp.spin == "ALPHA" and tmp.ldos == False:
            alpha_dos.append(tmp)
        elif tmp.spin == "BETA" and tmp.ldos == False:
            beta_dos.append(tmp)
        else:
            pass

    # plot alpha channel
    ax_num = len(alpha_dos) + 1
    fig = plt.figure(figsize=(12, 3*ax_num), dpi=100)
    gs = GridSpec(ax_num, 1, figure=fig, hspace=0)

    # total dos plot
    ax = fig.add_subplot(gs[0])
    dos, ener = alpha_dos[0].get_dos()
    ax.plot(ener, dos, label = "Total", color = "black", lw=lw)
    ax.set_xticklabels([])
    ax.set_xlim(-10,10)
    ax.set_ylim(ymin=0)
    ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    ax.legend(fontsize=fontsize)
    ymin, ymax = ax.get_ylim()

    # plot for other elements
    for i in range(1, ax_num):
        ax = fig.add_subplot(gs[i])
        dos_obj = alpha_dos[i-1]
        typical_orb = typical_orbital(dos_obj.element)
        dos, ener = dos_obj.get_dos(dos_type=typical_orb)
        ax.plot(ener, dos, label = dos_obj.element + " " + typical_orb, color = "C{0}".format(int(i)), lw=lw)
        if i == ax_num - 1:
            pass
        else:
            ax.set_xticklabels([])
        ax.set_xlim(-10,10)
        ax.set_ylim(ymin=0, ymax=ymax)
        ax.tick_params(axis='both', labelsize=fontsize, direction='in')
        ax.legend(fontsize=fontsize)

    # global figure setting
    fig.text(0.5, 0.04, 'Energy [eV]', ha='center', fontsize=fontsize)
    fig.text(0.04, 0.5, 'DOS [arb. unit]', va='center', fontsize=fontsize, rotation='vertical')

    fig.savefig("DOS_ALPHA.jpg", dpi=200)

    # plot beta channel
    ax_num = len(beta_dos) + 1
    fig = plt.figure(figsize=(12, 3*ax_num), dpi=100)
    gs = GridSpec(ax_num, 1, figure=fig, hspace=0)

    # total dos plot
    ax = fig.add_subplot(gs[0])
    dos, ener = beta_dos[0].get_dos()
    ax.plot(ener, dos, label = "Total", color = "black", lw=lw)
    ax.set_xticklabels([])
    ax.set_xlim(-10,10)
    ax.set_ylim(ymin=0)
    ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    ax.legend(fontsize=fontsize)
    ymin, ymax = ax.get_ylim()

    # plot for other elements
    for i in range(1, ax_num):
        ax = fig.add_subplot(gs[i])
        dos_obj = beta_dos[i-1]
        typical_orb = typical_orbital(dos_obj.element)
        dos, ener = dos_obj.get_dos(dos_type=typical_orb)
        ax.plot(ener, dos, label = dos_obj.element + " " + typical_orb, color = "C{0}".format(int(i)), lw=lw)
        if i == ax_num - 1:
            pass
        else:
            ax.set_xticklabels([])
        ax.set_xlim(-10,10)
        ax.set_ylim(ymin=0, ymax=ymax)
        ax.tick_params(axis='both', labelsize=fontsize, direction='in')
        ax.legend(fontsize=fontsize)

    fig.text(0.5, 0.04, 'Energy [eV]', ha='center', fontsize=fontsize)
    fig.text(0.04, 0.5, 'DOS [arb. unit]', va='center', fontsize=fontsize, rotation='vertical')
    fig.savefig("DOS_BETA.jpg", dpi=200)

def quick_plot_rks(pdos_dir):
    # parameter setting
    fontsize = 15
    lw = 1.5

    # find pdos files
    pdos_files = glob.glob(os.path.join(pdos_dir, "*pdos"))
    pdos_files.sort()

    #
    rks_dos = []
    for i in pdos_files:
        tmp = Pdos(i)
        if tmp.ldos == False:
            rks_dos.append(tmp)
        else:
            pass

    # plot
    ax_num = len(rks_dos) + 1
    fig = plt.figure(figsize=(12, 3*ax_num), dpi=100)
    gs = GridSpec(ax_num, 1, figure=fig, hspace=0)

    # total dos plot
    ax = fig.add_subplot(gs[0])
    dos, ener = rks_dos[0].get_dos()
    ax.plot(ener, dos, label = "Total", color = "black", lw=lw)
    ax.set_xticklabels([])
    ax.set_xlim(-10,10)
    ax.set_ylim(ymin=0)
    ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    ax.legend(fontsize=fontsize)
    ymin, ymax = ax.get_ylim()

    # plot for other elements
    for i in range(1, ax_num):
        ax = fig.add_subplot(gs[i])
        dos_obj = rks_dos[i-1]
        typical_orb = typical_orbital(dos_obj.element)
        dos, ener = dos_obj.get_dos(dos_type=typical_orb)
        ax.plot(ener, dos, label = dos_obj.element + " " + typical_orb, color = "C{0}".format(int(i)), lw=lw)
        if i == ax_num - 1:
            pass
        else:
            ax.set_xticklabels([])
        ax.set_xlim(-10,10)
        ax.set_ylim(ymin=0, ymax=ymax)
        ax.tick_params(axis='both', labelsize=fontsize, direction='in')
        ax.legend(fontsize=fontsize)

    # global figure setting
    fig.text(0.5, 0.04, 'Energy [eV]', ha='center', fontsize=fontsize)
    fig.text(0.04, 0.5, 'DOS [arb. unit]', va='center', fontsize=fontsize, rotation='vertical')

    fig.savefig("DOS.jpg", dpi=200)

