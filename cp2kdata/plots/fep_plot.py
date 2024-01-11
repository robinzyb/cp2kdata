import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from cp2kdata.block_parser.fep import parse_vertical_gap
from scipy import integrate
from cycler import cycler
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

au2eV = 2.72113838565563E+01


def get_cum_mean(array):
    tot = 0.0
    cum_mean_array = []
    for idx, i in enumerate(array):
        tot += i
        cum_mean_array.append(tot/(idx+1))
    cum_mean_array = np.array(cum_mean_array)
    return cum_mean_array


def plot_ti(fig_name):
    eta_sub_dir_list = glob.glob("[0-1].*")
    eta_sub_dir_list.sort()
    vgap_list, cum_vgap_list, ave_vgap_list = get_fep_gaps(eta_sub_dir_list)
    _plot_ti(eta_sub_dir_list, cum_vgap_list, ave_vgap_list, fig_name)


def get_fep_gaps(eta_sub_dir_list):
    vgap_list = []
    cum_vgap_list = []
    ave_vgap_list = []
    for eta in eta_sub_dir_list:
        mix_ener_file_list = glob.glob(f"{eta}/*-mix-1.ener")
        if len(mix_ener_file_list) == 0:
            continue
        vgap = parse_vertical_gap(mix_ener_file_list[0])*au2eV
        vgap_list.append(vgap)
        cum_vgap = get_cum_mean(vgap)
        cum_vgap_list.append(cum_vgap)
        ave_vgap_list.append(cum_vgap[-1])
    return vgap_list, cum_vgap_list, ave_vgap_list


def _plot_ti(eta_sub_dir_list, cum_vgap_list, ave_vgap_list, fig_name):

    dt = 0.0005

    eta_list = np.array(eta_sub_dir_list, dtype=float)
    # eta_list = np.array([0.25, 0.5, 1.0])
    N = len(eta_list)

    cmap = plt.cm.Reds(np.linspace(0.3, 0.9, N))
    custom_cycler = cycler("color", cmap)

    row = 1
    col = 2
    fig = plt.figure(figsize=(4.5*col, 6*row), dpi=150, facecolor='white')
    gs = fig.add_gridspec(row, col, wspace=0)
    ax = fig.add_subplot(gs[0])
    ax.set_prop_cycle(custom_cycler)
    max_time = 0
    for idx, eta in enumerate(eta_list):
        num_steps = len(cum_vgap_list[idx])

        time = np.arange(num_steps)*dt
        if time[-1] > max_time:
            max_time = time[-1]
        ax.plot(time, cum_vgap_list[idx])
        ax.text(time[-1]-0.4, ave_vgap_list[idx]+0.1,
                rf"$\langle \Delta E \rangle _{{{eta}}}$" + f": {ave_vgap_list[idx]:5.2f}", fontsize=15)
        # ax.text(time[-1]-0.4, ave_vgap_list[idx]+0.1, rf"$\eta$ = {eta}" + f": {ave_vgap_list[idx]:5.2f}", fontsize=15)
    ax.set_ylabel(r"$\langle \Delta E \rangle _{\eta}$ [eV]", fontsize=18)
    ax.set_xlabel("time [ps]", fontsize=18)
    ax.tick_params(direction='in', which='both')
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(AutoMinorLocator(10))
    ax.set_xlim(0, max_time+2.25)
    y_lim = ax.get_ylim()

    ax1 = fig.add_subplot(gs[1])
    ax1.plot(eta_list, ave_vgap_list, ls='--', color='C3')
    ax1.scatter(eta_list, ave_vgap_list, color=cmap,
                s=80, edgecolor='black', zorder=9)
    ax1.set_ylim(y_lim)
    # ax1.set_ylabel(r"$\langle \Delta E \rangle _{\eta}$ [eV]")
    ax1.set_xlabel(r"$\eta$", fontsize=18)
    ax1.set_yticklabels([])
    ax1.tick_params(direction='in', which='both')
    ax1.yaxis.set_major_locator(MultipleLocator(1))
    ax1.yaxis.set_minor_locator(AutoMinorLocator(10))

    # free energy
    fe = integrate.simpson(ave_vgap_list, np.array(eta_list, dtype=float))
    ax1.text(0.3, 0.85, r"$\mathrm{\Delta A_{FEP}}$ = " +
             f"{fe:5.3f} [eV]", transform=ax1.transAxes, fontsize=18)
    fig.tight_layout()
    fig.savefig(fig_name)
