from cp2kdata import Cp2kOutput
from cp2kdata import Cp2kPdos
from dpdata.unit import EnergyConversion, LengthConversion, PressureConversion
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import yaml
AU_TO_EV = EnergyConversion("hartree", "eV").value()
AU_TO_ANG = LengthConversion("bohr", "angstrom").value()
EV_ANG_m3_TO_GPa = PressureConversion("eV/angstrom^3", "GPa").value()


# -- plot cutoff results --#

def get_num_atoms(cutoff_test_sub_dir_list):
    cutoff_test_sub_dir = cutoff_test_sub_dir_list[0]
    output_name = "output*"
    output_name_list = glob.glob(
        os.path.join(cutoff_test_sub_dir, output_name))
    cutoff_out = Cp2kOutput(output_name_list[0])
    num_atoms = cutoff_out.get_num_atoms()
    return num_atoms


def get_cutoff_list(cutoff_test_sub_dir_list):
    cutoff_list = [
        float(cutoff_test_sub_dir.split(sep="_")[-1])
        for cutoff_test_sub_dir in cutoff_test_sub_dir_list
    ]
    return cutoff_list


def get_e_f_s(cp2k_out_name):
    print(f"Get Infromation from: {cp2k_out_name}")
    cutoff_out = Cp2kOutput(cp2k_out_name)
    ener = cutoff_out.get_energies_list()[-1]
    forces = cutoff_out.get_atomic_forces_list()[-1]
    stresses = cutoff_out.get_stress_tensor_list()[-1]
    return ener, forces, stresses


def get_multiple_e_f_s(cutoff_test_sub_dir_list):
    ener_list = []
    forces_list = []
    stresses_list = []
    for cutoff_test_sub_dir in cutoff_test_sub_dir_list:
        output_name = "output*"
        output_name_list = glob.glob(
            os.path.join(cutoff_test_sub_dir, output_name))
        ener, forces, stresses = get_e_f_s(output_name_list[0])
        ener_list.append(ener)
        forces_list.append(forces)
        stresses_list.append(stresses)
    return np.array(ener_list), np.array(forces_list), np.array(stresses_list)


def get_err_per_atom(array, num_atoms):
    err = np.diff(array, axis=0)
    return err/num_atoms


def get_matrix_rmse_and_max_err(matrix_list):
    err = np.diff(matrix_list, axis=0)
    se = np.square(err)
    mse = np.mean(se, axis=(1, 2))
    rmse = np.sqrt(mse)

    abs_err = np.abs(err)
    max_abs_err = np.max(abs_err, axis=(1, 2))
    return rmse, max_abs_err


def plot_axes_cutoff(cutoff_list, y_list, ax, idx):
    marker_cycle = ["o", "v", "d"]
    title_cycle = ["Energy", "Force", "Stress"]
    ylabel_cycle = ["error per atom [eV/atom]",
                    r"RMSE [eV$\cdot$A$^{-1}$]", r"RMSE [eV$\cdot$A$^{-3}$]"]

    fontdict = {"fontsize": 22}

    ax.plot(cutoff_list[1:], y_list, color=f"C{idx}",
            marker=marker_cycle[idx], markeredgecolor="black")

    # ylim = ax.get_ylim()
    ax.ticklabel_format(style='plain', useOffset=False)
    ax.tick_params(direction="in")
    # ax.set_xticks(cutoff_list)
    # ax.set_xticklabels(cutoff_list)
    ax.set_title(title_cycle[idx], fontdict=fontdict)
    ax.set_xlabel("Cutoff [Ry]", fontdict=fontdict)
    ax.set_ylabel(ylabel_cycle[idx], fontdict=fontdict)


def plot_cutoff_test(target_dir="."):
    cutoff_test_sub_dir_list = glob.glob(os.path.join(target_dir, "cutoff_*"))
    cutoff_test_sub_dir_list.sort()
    num_atoms = get_num_atoms(cutoff_test_sub_dir_list)
    cutoff_list = get_cutoff_list(cutoff_test_sub_dir_list)
    ener_list, forces_list, stresses_list = get_multiple_e_f_s(
        cutoff_test_sub_dir_list)
    ener_err_per_atom = get_err_per_atom(ener_list * AU_TO_EV, num_atoms)
    forces_rmse, forces_max_err = get_matrix_rmse_and_max_err(
        forces_list * AU_TO_EV/AU_TO_ANG)
    stresses_rmse, stresses_max_err = get_matrix_rmse_and_max_err(
        stresses_list/EV_ANG_m3_TO_GPa)

    test_collect = (ener_err_per_atom, forces_rmse, stresses_rmse)

    plt.rc('font', size=18)
    plt.rc('axes', titlesize=23)  # fontsize of the title
    plt.rc('axes', labelsize=20)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=18)  # fontsize of the x tick labels
    plt.rc('ytick', labelsize=18)  # fontsize of the y tick labels
    plt.rc('legend', fontsize=16)  # fontsize of the legend
    plt.rc('lines', linewidth=2, markersize=10)  # controls default text size
    plt.rc('axes', linewidth=2)
    plt.rc('xtick.major', size=10, width=2)
    plt.rc('ytick.major', size=10, width=2)

    row = 1
    col = 3
    fig = plt.figure(figsize=(8*col, 5.5*row), dpi=150, facecolor='white')
    gs = fig.add_gridspec(row, col)

    for idx, param_list in enumerate(test_collect):
        ax = fig.add_subplot(gs[idx])
        if param_list is None:
            ax.axis('off')
            # ax.text("Place Holder")
            continue
        plot_axes_cutoff(cutoff_list, param_list, ax, idx)

    fig.tight_layout()
    fig.savefig("results_cutoff_test.pdf")

# -- plot basis results --#


def basis_dir_name_converter(basis_test_sub_dir):
    name_split_list = basis_test_sub_dir.split(sep="-")
    if "SR" in name_split_list:
        basis_name = name_split_list[0].split(sep="_")[1] + "-SR"
    else:
        basis_name = name_split_list[0].split(sep="_")[1]
    return basis_name


def basis_name_order(basis_name):
    BASIS_ORDER = {
        "SZV-SR": 0,
        "SZV": 1,
        "DZVP-SR": 2,
        "DZVP": 3,
        "TZVP-SR": 4,
        "TZVP": 5,
        "TZV2P-SR": 6,
        "TZV2P": 7,
        "TZV2PX-SR": 8,
        "TZV2PX": 9
    }

    return BASIS_ORDER[basis_name]


def basis_dir_name_order(basis_dir_name):
    basis_name = basis_dir_name_converter(basis_dir_name)
    return basis_name_order(basis_name)


def get_basis_name_list(basis_test_sub_dir_list):

    basis_list = []
    for basis_test_sub_dir in basis_test_sub_dir_list:
        basis_name = basis_dir_name_converter(basis_test_sub_dir)
        basis_list.append(basis_name)

    return basis_list


def plot_axes_basis(basis_list, y_list, ax, idx):
    marker_cycle = ["o", "v", "d"]
    title_cycle = ["Energy", "Force", "Stress"]
    ylabel_cycle = ["error per atom [eV/atom]",
                    r"RMSE [eV$\cdot$A$^{-1}$]", r"RMSE [eV$\cdot$A$^{-3}$]"]

    fontdict = {"fontsize": 22}

    x_list = list(range(len(basis_list)))

    ax.plot(x_list[1:], y_list, color=f"C{idx}",
            marker=marker_cycle[idx], markeredgecolor="black")
    # print(len(y_list))

    # ylim = ax.get_ylim()
    ax.ticklabel_format(style='plain', useOffset=False)
    ax.tick_params(direction="in")
    ax.set_xticks(x_list)
    ax.set_xticklabels(basis_list)
    ax.set_title(title_cycle[idx], fontdict=fontdict)
    ax.set_xlabel("Basis Set", fontdict=fontdict)
    ax.set_ylabel(ylabel_cycle[idx], fontdict=fontdict)


def plot_basis_test(target_dir="."):
    target_dir = "."
    basis_test_sub_dir_list = glob.glob(os.path.join(target_dir, "basis_*"))
    basis_test_sub_dir_list.sort(key=basis_dir_name_order)

    num_atoms = get_num_atoms(basis_test_sub_dir_list)
    basis_list = get_basis_name_list(basis_test_sub_dir_list)
    ener_list, forces_list, stresses_list = get_multiple_e_f_s(
        basis_test_sub_dir_list)
    ener_err_per_atom = get_err_per_atom(ener_list * AU_TO_EV, num_atoms)
    forces_rmse, forces_max_err = get_matrix_rmse_and_max_err(
        forces_list * AU_TO_EV/AU_TO_ANG)
    stresses_rmse, stresses_max_err = get_matrix_rmse_and_max_err(
        stresses_list/EV_ANG_m3_TO_GPa)

    test_collect = (ener_err_per_atom, forces_rmse, stresses_rmse)

    plt.rc('font', size=18)
    plt.rc('axes', titlesize=23)  # fontsize of the title
    plt.rc('axes', labelsize=20)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=18)  # fontsize of the x tick labels
    plt.rc('ytick', labelsize=18)  # fontsize of the y tick labels
    plt.rc('legend', fontsize=16)  # fontsize of the legend
    plt.rc('lines', linewidth=2, markersize=10)  # controls default text size
    plt.rc('axes', linewidth=2)
    plt.rc('xtick.major', size=10, width=2)
    plt.rc('ytick.major', size=10, width=2)

    row = 1
    col = 3
    fig = plt.figure(figsize=(8*col, 5.5*row), dpi=150, facecolor='white')
    gs = fig.add_gridspec(row, col)

    for idx, param_list in enumerate(test_collect):
        ax = fig.add_subplot(gs[idx])
        if param_list is None:
            ax.axis('off')
            # ax.text("Place Holder")
            continue
        plot_axes_basis(basis_list, param_list, ax, idx)

    fig.tight_layout()
    fig.savefig("results_basis_test.pdf")

# -- plot U results --#


def get_U_list(U_test_sub_dir_list):
    U_list = [
        float(U_test_sub_dir.split(sep="_")[-1])
        for U_test_sub_dir in U_test_sub_dir_list
    ]
    return U_list


def get_cell_param(cp2k_out):
    from ase.cell import Cell
    opt_cell = cp2k_out.get_all_cells()[-1]
    opt_cell = Cell(opt_cell)
    a, b, c, alpha, beta, gamma = opt_cell.cellpar()
    return a, b, c, alpha, beta, gamma


def get_multiple_cell_param(U_test_sub_dir_list):
    a_list = []
    b_list = []
    c_list = []
    alpha_list = []
    beta_list = []
    gamma_list = []

    for U_test_sub_dir in U_test_sub_dir_list:

        output_name_list = glob.glob(os.path.join(U_test_sub_dir, "output*"))

        cp2k_out = Cp2kOutput(os.path.basename(
            output_name_list[0]), path_prefix=U_test_sub_dir)

        a, b, c, alpha, beta, gamma = get_cell_param(cp2k_out)
        a_list.append(a)
        b_list.append(b)
        c_list.append(c)
        alpha_list.append(alpha)
        beta_list.append(beta)
        gamma_list.append(gamma)
    return np.array(a_list), np.array(b_list), np.array(c_list), np.array(alpha_list), np.array(beta_list), np.array(gamma_list)


def get_dos_param(cp2k_pdos):

    homo = cp2k_pdos.get_homo_ener()
    lumo = cp2k_pdos.get_lumo_ener()
    return homo, lumo


def get_min_gap(U_test_sub_dir):
    a_pdos_list = glob.glob(os.path.join(U_test_sub_dir, "*ALPHA*pdos"))
    a_pdos = Cp2kPdos(a_pdos_list[0])
    a_homo, a_lumo = get_dos_param(cp2k_pdos=a_pdos)
    b_pdos_list = glob.glob(os.path.join(U_test_sub_dir, "*BETA*pdos"))
    b_pdos = Cp2kPdos(b_pdos_list[0])
    b_homo, b_lumo = get_dos_param(cp2k_pdos=b_pdos)
    if a_homo > b_homo:
        homo = a_homo
    else:
        homo = b_homo

    if a_lumo < b_lumo:
        lumo = a_lumo
    else:
        lumo = b_lumo
    return lumo - homo


def get_multiple_min_gap(U_test_sub_dir_list):
    gap_list = []
    for U_test_sub_dir in U_test_sub_dir_list:
        gap = get_min_gap(U_test_sub_dir)
        gap_list.append(gap)

    return np.array(gap_list)

    # homo_list = np.array(homo_list)
    # lumo_list = np.array(lumo_list)


def plot_axes_U(U_list, y_list, ax, idx):
    marker_cycle = ["o", "o", "o", "o", "v", "d", "s", "p", "h"]
    title_cycle = ["band gap", "p1", "p2", "a",
                   "b", "c", "alpha", "beta", "gamma"]
    ylabel_cycle = ["energy [eV]", "length [A]", "length [A]", "length [A]",
                    "length [A]", "length [A]", "angle [deg]", "angle [deg]", "angle [deg]"]

    fontdict = {"fontsize": 22}

    ax.plot(U_list, y_list,
            color=f"C{idx}", marker=marker_cycle[idx], markeredgecolor="black")

    # ylim = ax.get_ylim()
    ax.ticklabel_format(style='plain', useOffset=False)
    ax.tick_params(direction="in")
    ax.set_xticks(U_list)
    ax.set_xticklabels(U_list)
    ax.set_title(title_cycle[idx], fontdict=fontdict)
    ax.set_xlabel("U [eV]", fontdict=fontdict)
    ax.set_ylabel(ylabel_cycle[idx], fontdict=fontdict)


def plot_axes_exp(exp_value, ax, idx):
    if exp_value is None:
        pass
    elif type(exp_value) is float or type(exp_value) is int:
        ax.axhline(exp_value, color=f"C{idx+1}", ls='--', lw=2)
    elif (type(exp_value) is list) and (len(exp_value) == 2):
        ax.axhspan(exp_value[0], exp_value[1], color=f'C{idx+1}', alpha=0.5)


def plot_U_test(
    target_dir=".",
    exp_collect=(None, None, None, None, None, None, None, None, None)
):
    U_test_sub_dir_list = glob.glob(os.path.join(target_dir, "U_*"))
    U_test_sub_dir_list.sort()
    U_list = get_U_list(U_test_sub_dir_list)
    gap_collect = get_multiple_min_gap(U_test_sub_dir_list)
    property_collect = (gap_collect, None, None)
    cell_param_collect = get_multiple_cell_param(U_test_sub_dir_list)

    total_collect = property_collect + cell_param_collect

    plt.rc('font', size=18)
    plt.rc('axes', titlesize=23)  # fontsize of the title
    plt.rc('axes', labelsize=20)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=18)  # fontsize of the x tick labels
    plt.rc('ytick', labelsize=18)  # fontsize of the y tick labels
    plt.rc('legend', fontsize=16)  # fontsize of the legend
    plt.rc('lines', linewidth=2, markersize=10)  # controls default text size
    plt.rc('axes', linewidth=2)
    plt.rc('xtick.major', size=10, width=2)
    plt.rc('ytick.major', size=10, width=2)

    row = 3
    col = 3
    fig = plt.figure(figsize=(8*col, 5.5*row), dpi=150, facecolor='white')
    gs = fig.add_gridspec(row, col)

    for idx, param_list in enumerate(total_collect):
        ax = fig.add_subplot(gs[idx])
        if param_list is None:
            ax.axis('off')
            # ax.text("Place Holder")
            continue
        plot_axes_U(U_list, param_list, ax, idx)
        plot_axes_exp(exp_collect[idx], ax, idx)

    fig.tight_layout()
    fig.savefig("results_U_test.pdf")


def get_exp_collect_from_yaml(yaml_file):
    with open(yaml_file, "r") as fp:
        exp_dict = yaml.safe_load(fp)
    exp_collect = (
        exp_dict.get("gap", None),
        exp_dict.get("prop1", None),
        exp_dict.get("prop2", None),
        exp_dict.get("cell", {}).get("a", None),
        exp_dict.get("cell", {}).get("b", None),
        exp_dict.get("cell", {}).get("c", None),
        exp_dict.get("cell", {}).get("alpha", None),
        exp_dict.get("cell", {}).get("beta", None),
        exp_dict.get("cell", {}).get("gamma", None)
    )
    return exp_collect
