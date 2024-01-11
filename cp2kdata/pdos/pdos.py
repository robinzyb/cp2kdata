import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import regex as re
from matplotlib.gridspec import GridSpec
from scipy.ndimage import gaussian_filter1d

from cp2kdata.utils import au2eV

atomic_color_map = {
    'Ac': (0.39344, 0.62101, 0.45034),
    'Ag': (0.72032, 0.73631, 0.74339),
    'Al': (0.50718, 0.70056, 0.84062),
    'Am': (0.3, 0.3, 0.3),
    'Ar': (0.81349, 0.99731, 0.77075),
    'As': (0.45814, 0.81694, 0.34249),
    'At': (0.0, 0.0, 1.0),
    'Au': (0.99628, 0.70149, 0.22106),
    'B': (0.1249, 0.63612, 0.05948),
    'Ba': (0.11835, 0.93959, 0.17565),
    'Be': (0.37147, 0.8459, 0.48292),
    'Bi': (0.82428, 0.18732, 0.97211),
    'Br': (0.49645, 0.19333, 0.01076),
    'C': (0.5043, 0.28659, 0.16236),
    'Ca': (0.35642, 0.58863, 0.74498),
    'Cd': (0.95145, 0.12102, 0.86354),
    'Ce': (0.82055, 0.99071, 0.02374),
    'Cl': (0.19583, 0.98828, 0.01167),
    'Co': (0.0, 0.0, 0.68666),
    'Cr': (0.0, 0.0, 0.62),
    'Cs': (0.05872, 0.99922, 0.72578),
    'Cu': (0.1339, 0.28022, 0.86606),
    'D': (0.8, 0.8, 1.0),
    'Dy': (0.1939, 0.02374, 0.99071),
    'Er': (0.28688, 0.45071, 0.23043),
    'Eu': (0.98367, 0.03078, 0.83615),
    'F': (0.69139, 0.72934, 0.9028),
    'Fe': (0.71051, 0.44662, 0.00136),
    'Fr': (0.0, 0.0, 0.0),
    'Ga': (0.62292, 0.89293, 0.45486),
    'Gd': (0.75325, 0.01445, 1.0),
    'Ge': (0.49557, 0.43499, 0.65193),
    'H': (1.0, 0.8, 0.8),
    'He': (0.98907, 0.91312, 0.81091),
    'Hf': (0.70704, 0.70552, 0.3509),
    'Hg': (0.8294, 0.72125, 0.79823),
    'Ho': (0.02837, 0.25876, 0.98608),
    'I': (0.55914, 0.122, 0.54453),
    'In': (0.84378, 0.50401, 0.73483),
    'Ir': (0.78975, 0.81033, 0.45049),
    'K': (0.63255, 0.13281, 0.96858),
    'Kr': (0.98102, 0.75805, 0.95413),
    'La': (0.3534, 0.77057, 0.28737),
    'Li': (0.52731, 0.87953, 0.4567),
    'Lu': (0.15097, 0.99391, 0.71032),
    'Mg': (0.98773, 0.48452, 0.0847),
    'Mn': (0.66148, 0.03412, 0.62036),
    'Mo': (0.70584, 0.52602, 0.68925),
    'N': (0.69139, 0.72934, 0.9028),
    'Na': (0.97955, 0.86618, 0.23787),
    'Nb': (0.29992, 0.70007, 0.46459),
    'Nd': (0.98701, 0.5556, 0.02744),
    'Ne': (0.99954, 0.21788, 0.71035),
    'Ni': (0.72032, 0.73631, 0.74339),
    'Np': (0.3, 0.3, 0.3),
    'O': (0.99997, 0.01328, 0.0),
    'Os': (0.78703, 0.69512, 0.47379),
    'P': (0.75557, 0.61256, 0.76425),
    'Pa': (0.16101, 0.98387, 0.20855),
    'Pb': (0.32386, 0.32592, 0.35729),
    'Pd': (0.75978, 0.76818, 0.72454),
    'Pm': (0.0, 0.0, 0.96),
    'Po': (0.0, 0.0, 1.0),
    'Pr': (0.9913, 0.88559, 0.02315),
    'Pt': (0.79997, 0.77511, 0.75068),
    'Pu': (0.3, 0.3, 0.3),
    'Ra': (0.42959, 0.66659, 0.34786),
    'Rb': (1.0, 0.0, 0.6),
    'Re': (0.70294, 0.69401, 0.55789),
    'Rh': (0.80748, 0.82205, 0.67068),
    'Rn': (1.0, 1.0, 0.0),
    'Ru': (0.81184, 0.72113, 0.68089),
    'S': (1.0, 0.98071, 0.0),
    'Sb': (0.84627, 0.51498, 0.31315),
    'Sc': (0.71209, 0.3893, 0.67279),
    'Se': (0.6042, 0.93874, 0.06122),
    'Si': (0.10596, 0.23226, 0.98096),
    'Sm': (0.99042, 0.02403, 0.49195),
    'Sn': (0.60764, 0.56052, 0.72926),
    'Sr': (0.0, 1.0, 0.15259),
    'Ta': (0.71952, 0.60694, 0.33841),
    'Tb': (0.44315, 0.01663, 0.99782),
    'Tc': (0.80574, 0.68699, 0.79478),
    'Te': (0.67958, 0.63586, 0.32038),
    'Th': (0.14893, 0.99596, 0.47106),
    'Ti': (0.47237, 0.79393, 1.0),
    'Tl': (0.58798, 0.53854, 0.42649),
    'Tm': (0.0, 0.0, 0.88),
    'U': (0.47774, 0.63362, 0.66714),
    'V': (0.9, 0.1, 0.0),
    'W': (0.55616, 0.54257, 0.50178),
    'XX': (0.3, 0.3, 0.3),
    'Xe': (0.60662, 0.63218, 0.97305),
    'Y': (0.40259, 0.59739, 0.55813),
    'Yb': (0.15323, 0.99165, 0.95836),
    'Zn': (0.56123, 0.56445, 0.50799),
    'Zr': (0.0, 1.0, 0.0)}

# input the element and return typical orbital in dos
# for example d for Ti, s for H, p for O
typical_orbital = {
    "H": "s",
    "He": "s",
    "Na": "s",
    "K": "s",
    "Rb": "s",
    "Cs": "s",
    "Be": "s",
    "Mg": "s",
    "Ca": "s",
    "Sr": "s",
    "Ba": "s",
    "O": "p",
    "S": "p",
    "Se": "p",
    "Te": "p",
    "N": "p",
    "P": "p",
    "As": "p",
    "Sb": "p",
    "Bi": "p",
    "C": "p",
    "Si": "p",
    "Ge": "p",
    "Sn": "p",
    "Pb": "p",
    "B": "p",
    "Al": "p",
    "Ga": "p",
    "In": "p",
    "Tl": "p",
    "F": "p",
    "Cl": "p",
    "Br": "p",
    "I": "p",
    "Sc": "d",
    "Ti": "d",
    "V": "d",
    "Cr": "d",
    "Mn": "d",
    "Fe": "d",
    "Co": "d",
    "Ni": "d",
    "Cu": "d",
    "Zn": "d",
    "Y": "d",
    "Zr": "d",
    "Nb": "d",
    "Mo": "d",
    "Te": "d",
    "Ru": "d",
    "Rh": "d",
    "Pd": "d",
    "Ag": "d",
    "Cd": "d",
    "Hf": "d",
    "Ta": "d",
    "W": "d",
    "Re": "d",
    "Os": "d",
    "Ir": "d",
    "Pt": "d",
    "Au": "d",
    "Hg": "d",
    "La": "f",
    "Ce": "f",
    "Pr": "f"
}


class Cp2kPdos():
    def __init__(self, file_name, parse_file_name=True):
        self.file = file_name
        self.element = self.read_dos_element()
        self.fermi = self.read_dos_fermi()
        self.energies = self.read_dos_energies()
        if parse_file_name:
            self.project_name, self.spin, self.listidx, self.kind, self.timestep = pdos_name_parser(
                self.file)

    def read_dos_element(self):
        with open(self.file) as f:
            first_line = f.readline()
            element = first_line.split()[6]
#        element = ''.join([i for i in self.kind if not i.isdigit()])
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

    @property
    def occupation(self):
        occupation = np.loadtxt(self.file, usecols=2)

        return occupation

    def get_homo_ener(self):
        homo_idx = np.where(self.occupation == 0)[0][0]-1
        homo_ener = self.energies[homo_idx]

        return homo_ener

    def get_lumo_ener(self):
        lumo_ener = self.energies[self.occupation == 0][0]
        return lumo_ener

    def get_raw_dos(self, dos_type="total", steplen=0.1):

        file = self.file
        energies = self.energies
        fermi = self.fermi
        steplen = 0.1

        if dos_type == "total":
            tmp_len = len(np.loadtxt(file, usecols=2))
            weights = np.ones(tmp_len)
        elif dos_type == "s":
            weights = np.loadtxt(file, usecols=3)
        elif dos_type == "p":
            weights = np.loadtxt(file, usecols=(4, 5, 6)).sum(axis=1)
        elif dos_type == "d":
            weights = np.loadtxt(file, usecols=(7, 8, 9, 10, 11)).sum(axis=1)
        elif dos_type == "f":
            weights = np.loadtxt(file, usecols=(
                12, 13, 14, 15, 16, 17, 18)).sum(axis=1)
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


PDOS_NAME_RE = re.compile(
    r"""
    (?P<project_name>\S+)-((?P<spin>(ALPHA|BETA))_)?(list(?P<listidx>\d+))?(k(?P<kind>\d+))?-1(_(?P<step>\d+))?.pdos$
    """,
    re.VERBOSE
)


def pdos_name_parser(filename):
    # used to parse pdos filename
    filename = os.path.basename(filename)
    match = PDOS_NAME_RE.match(filename)

    project_name = match["project_name"]
    spin = match["spin"]
    listidx = match["listidx"]
    kind = match["kind"]
    step = match["step"]

    return project_name, spin, listidx, kind, step


def quick_plot_uks(pdos_dir, style=0, replace_dict=None):
    # default plot parameters setting
    plt.rc('font', size=18)  # controls default text size
    plt.rc('axes', titlesize=23)  # fontsize of the title
    plt.rc('axes', labelsize=20)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=18)  # fontsize of the x tick labels
    plt.rc('ytick', labelsize=18)  # fontsize of the y tick labels
    plt.rc('legend', fontsize=16)  # fontsize of the legend

    plt.rc('lines', linewidth=2, markersize=10)  # controls default text size

    plt.rc('axes', linewidth=2)
    plt.rc('xtick.major', size=10, width=2)
    plt.rc('ytick.major', size=10, width=2)

    # find pdos files
    pdos_files = glob.glob(os.path.join(pdos_dir, "*pdos"))
    pdos_files.sort()

    data = {
        'ALPHA': [],
        'BETA': []
    }
    #
    for i in pdos_files:
        tmp = Cp2kPdos(i)
        if tmp.listidx is None:
            data[tmp.spin].append(tmp)

    fig = plt.figure(figsize=(8, 5), dpi=200)
    ax = fig.add_subplot(111)
    raw = True
    legend_handles = []
    legend_labels = []

    for pdosobj in data['ALPHA']:
        true_element = get_true_element(
            pdosobj=pdosobj, replace_dict=replace_dict)
        l1, label = plot_single_pdos(
            pdosobj, ax, true_element, spin=1, raw=raw)
        legend_handles.append(l1)
        legend_labels.append(label)

    for pdosobj in data['BETA']:
        true_element = get_true_element(
            pdosobj=pdosobj, replace_dict=replace_dict)
        plot_single_pdos(pdosobj, ax, true_element, spin=-1, raw=raw)

    ax.axvline(x=0, color="gray", alpha=.8, ls="-.")
    ax.text(0.05, 0.8, "ALPHA", ha="left",
            va="center", transform=ax.transAxes,)
    ax.text(0.05, 0.2, "BETA", ha="left", va="center", transform=ax.transAxes,)
    ax.legend(legend_handles, legend_labels,)
    ax.set_xlim(-10, 10)
    ax.set_xlabel("Energy [eV]",)
    ax.set_ylabel("DOS [arb. unit]",)

    fig.tight_layout()
    fig.savefig("DOS_Plot.pdf", format="pdf")
    # plot alpha channel
    # ax_num = len(alpha_dos) + 1
    # fig = plt.figure(figsize=(12, 3*ax_num), dpi=100)
    # gs = GridSpec(ax_num, 1, figure=fig, hspace=0)
#
    # total dos plot
    # ax = fig.add_subplot(gs[0])
    # dos, ener = alpha_dos[0].get_dos()
    # ax.plot(ener, dos, label = "Total", color = "black", lw=lw)
    # ax.set_xticklabels([])
    # ax.set_xlim(-10,10)
    # ax.set_ylim(ymin=0)
    # ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    # ax.legend(fontsize=fontsize)
    # ymin, ymax = ax.get_ylim()
#
    # plot for other elements
    # for i in range(1, ax_num):
    #    ax = fig.add_subplot(gs[i])
    #    dos_obj = alpha_dos[i-1]
    #    typical_orb = typical_orbital(dos_obj.element)
    #    dos, ener = dos_obj.get_dos(dos_type=typical_orb)
    #    ax.plot(ener, dos, label = dos_obj.element + " " + typical_orb, color = "C{0}".format(int(i)), lw=lw)
    #    if i == ax_num - 1:
    #        pass
    #    else:
    #        ax.set_xticklabels([])
    #    ax.set_xlim(-10,10)
    #    ax.set_ylim(ymin=0, ymax=ymax)
    #    ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    #    ax.legend(fontsize=fontsize)
#
    # global figure setting
    # fig.text(0.5, 0.04, 'Energy [eV]', ha='center', fontsize=fontsize)
    # fig.text(0.04, 0.5, 'DOS [arb. unit]', va='center', fontsize=fontsize, rotation='vertical')
#
    # fig.savefig("DOS_ALPHA.jpg", dpi=200)
#
    # plot beta channel
    # ax_num = len(beta_dos) + 1
    # fig = plt.figure(figsize=(12, 3*ax_num), dpi=100)
    # gs = GridSpec(ax_num, 1, figure=fig, hspace=0)
#
    # total dos plot
    # ax = fig.add_subplot(gs[0])
    # dos, ener = beta_dos[0].get_dos()
    # ax.plot(ener, dos, label = "Total", color = "black", lw=lw)
    # ax.set_xticklabels([])
    # ax.set_xlim(-10,10)
    # ax.set_ylim(ymin=0)
    # ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    # ax.legend(fontsize=fontsize)
    # ymin, ymax = ax.get_ylim()
#
    # plot for other elements
    # for i in range(1, ax_num):
    #    ax = fig.add_subplot(gs[i])
    #    dos_obj = beta_dos[i-1]
    #    typical_orb = typical_orbital(dos_obj.element)
    #    dos, ener = dos_obj.get_dos(dos_type=typical_orb)
    #    ax.plot(ener, dos, label = dos_obj.element + " " + typical_orb, color = "C{0}".format(int(i)), lw=lw)
    #    if i == ax_num - 1:
    #        pass
    #    else:
    #        ax.set_xticklabels([])
    #    ax.set_xlim(-10,10)
    #    ax.set_ylim(ymin=0, ymax=ymax)
    #    ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    #    ax.legend(fontsize=fontsize)
#
    # fig.text(0.5, 0.04, 'Energy [eV]', ha='center', fontsize=fontsize)
    # fig.text(0.04, 0.5, 'DOS [arb. unit]', va='center', fontsize=fontsize, rotation='vertical')
    # fig.savefig("DOS_BETA.jpg", dpi=200)


def get_true_element(pdosobj, replace_dict=None):
    if replace_dict:
        true_element = replace_dict.get(pdosobj.element, pdosobj.element)
    else:
        true_element = pdosobj.element
    return true_element


def plot_single_pdos(pdosobj, ax, true_element, spin=1, raw=True):

    to = typical_orbital.get(true_element)
    label = true_element + "-" + to

    if raw:
        pdos, ener = pdosobj.get_raw_dos(dos_type=to)
    else:
        pdos, ener = pdosobj.get_dos(dos_type=to, sigma=0.5)

    pdos *= spin
    color = atomic_color_map.get(true_element)
    l1, = ax.plot(ener, pdos, color=color, lw=2., label=label)

    return l1, label


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
        tmp = Cp2kPdos(i)
        rks_dos.append(tmp)
        # if tmp.ldos == False:
        #    rks_dos.append(tmp)
        # else:
        #    pass

    # plot
    ax_num = len(rks_dos) + 1
    fig = plt.figure(figsize=(12, 3*ax_num), dpi=100)
    gs = GridSpec(ax_num, 1, figure=fig, hspace=0)

    # total dos plot
    ax = fig.add_subplot(gs[0])
    dos, ener = rks_dos[0].get_dos()
    ax.plot(ener, dos, label="Total", color="black", lw=lw)
    ax.set_xticklabels([])
    ax.set_xlim(-10, 10)
    ax.set_ylim(ymin=0)
    ax.tick_params(axis='both', labelsize=fontsize, direction='in')
    ax.legend(fontsize=fontsize)
    ymin, ymax = ax.get_ylim()

    # plot for other elements
    for i in range(1, ax_num):
        ax = fig.add_subplot(gs[i])
        dos_obj = rks_dos[i-1]
        typical_orb = typical_orbital.get(dos_obj.element)
        dos, ener = dos_obj.get_dos(dos_type=typical_orb)
        ax.plot(ener, dos, label=dos_obj.element + " " +
                typical_orb, color="C{0}".format(int(i)), lw=lw)
        if i == ax_num - 1:
            pass
        else:
            ax.set_xticklabels([])
        ax.set_xlim(-10, 10)
        ax.set_ylim(ymin=0, ymax=ymax)
        ax.tick_params(axis='both', labelsize=fontsize, direction='in')
        ax.legend(fontsize=fontsize)

    # global figure setting
    fig.text(0.5, 0.04, 'Energy [eV]', ha='center', fontsize=fontsize)
    fig.text(0.04, 0.5, 'DOS [arb. unit]', va='center',
             fontsize=fontsize, rotation='vertical')

    fig.savefig("DOS.jpg", dpi=200)
