import sys

import matplotlib.pyplot as plt
import time
import numpy as np
from matplotlib.gridspec import GridSpec

from .block_parser.dft_plus_u import parse_dft_plus_u_occ
from .block_parser.forces import parse_atomic_forces_list
from .block_parser.geo_opt import parse_geo_opt
from .block_parser.header_info import parse_dft, parse_global, parse_header
from .block_parser.hirshfeld import parse_hirshfeld_pop_list
from .block_parser.mulliken import parse_mulliken_pop_list
from .block_parser.energies import parse_energies_list
from .block_parser.coordinates import parse_init_atomic_coordinates
from .block_parser.atomic_kind import parse_atomic_kinds
from .block_parser.errors_handle import parse_errors
from .block_parser.stress import parse_stress_tensor_list
from .block_parser.cells import parse_init_cell

def check_run_type(run_type):
    implemented_run_type_parsers = ["ENERGY_FORCE", "ENERGY", "MD", "GEO_OPT"]
    if run_type in implemented_run_type_parsers:
        pass
    else:
        raise ValueError


class Cp2kOutput:
    """Class for parsing cp2k output"""

    def __init__(self, output_file, ignore_error=False):
        # change a way to do, not skipping way!
        with open(output_file, 'r') as fp:
        #    header_idx = []
        #    for idx, ii in enumerate(fp):
        #        if 'Multiplication driver' in ii:
        #            header_idx.append(idx)
        #    fp.seek(0)
        #    all_lines = []
        #    for idx, ii in enumerate(fp):
        #        if idx >= header_idx[-1]:
        #            all_lines.append(ii)
            #self.output_file = "".join(all_lines)
            self.output_file = "".join(fp.readlines())
        self.header_info = parse_header(self.output_file)
        self.global_info = parse_global(self.output_file)
        self.dft_info = parse_dft(self.output_file)
        try:
            check_run_type(self.global_info["run_type"])
        except ValueError:
            print(
                (
                    "Parser for Run Type {0} Haven't Been Implemented Yet!".format(
                        self.global_info["run_type"])
                )
            )
            sys.exit()
            
        #self.errors_info = parse_errors(self.output_file)
        #if ignore_error:
        #    pass
        #else:
        #    if self.errors_info:
        #        if self.errors_info.get("exceed_wall_time", None):
        #            raise ValueError("Your output exceeds wall time, it might be incomplete, if you want to continue, please add set Cp2kOutput(output, ignore_error=True)")
        
        if self.global_info["run_type"] == "ENERGY_FORCE":
            self.num_frames = 1
        elif self.global_info["run_type"] == "GEO_OPT":
            # parse global info

            self.geo_opt_info = parse_geo_opt(self.output_file)
            self.num_frames = len(self.geo_opt_info)
        else:
            self.geo_opt_info = None
        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.init_cell = parse_init_cell(self.output_file)
        self.energies_list = parse_energies_list(self.output_file)

        self.atomic_kind = parse_atomic_kinds(self.output_file)
        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.stress_tensor_list = parse_stress_tensor_list(self.output_file)
        self.mulliken_pop_list = parse_mulliken_pop_list(
            self.output_file, self.dft_info)
        self.hirshfeld_pop_list = parse_hirshfeld_pop_list(self.output_file)
        self.dft_plus_u_occ = parse_dft_plus_u_occ(self.output_file)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        txt = "\n"
        txt += "Cp2k Output Summary\n"
        txt += "\n"
        txt += "--------------------------------------\n"
        txt += "\n"
        txt += "Cp2k Version       : {0:.1f}\n".format(self.get_version_string())
        txt += "\n"
        txt += "Run Type           : {0:s}\n".format(self.get_run_type())
        txt += "\n"
        txt += "Atom Numbers       : {0:d}\n".format(self.get_num_atoms())
        txt += "\n"
        txt += "Frame Numbers      : {0:d}\n".format(self.get_num_frames())
        txt += "\n"
        txt += "Force in Output    : {0:s}\n".format(self.get_force_status())
        txt += "\n"
        txt += "Stress in Output   : {0:s}\n".format(self.get_stress_status())
        txt += "\n"
        txt += "Element List       : "
        for ii in self.get_atomic_kind():
            txt += "{0:5s}".format(str(ii))
        txt += "\n"*2
        txt += "Element Numb       : "
        for ii in self.get_atom_num():
            txt += "{0:5s}".format(str(ii))
        txt += "\n"
        txt += "--------------------------------------\n"
        return txt

    def get_version_string(self) -> float:
        return self.header_info["version_string"]

    def get_run_type(self) -> float:
        return self.global_info["run_type"]

    def get_init_cell(self):
        return self.init_cell

    def get_energies_list(self):
        return self.energies_list

    def get_atomic_kind(self):
        return self.atomic_kind
    
    def get_atom_num(self):
        # kind idx is arrange from low to high
        kind_idx, counts = np.unique(
            self.get_atom_kinds_list(), 
            return_counts=True
            )
        return counts
            

    def get_atom_kinds_list(self):
        return self.atom_kind_list

    def get_atomic_kind(self):
        return self.atomic_kind

    def get_chemical_symbols(self):
        return self.chemical_symbols

    def get_chemical_symbols_fake(self):
        return self.atomic_kind[self.atom_kind_list-1]

    def get_init_atomic_coordinates(self):
        return self.init_atomic_coordinates

    def get_num_atoms(self):
        return len(self.chemical_symbols)

    def get_num_frames(self):
        return self.num_frames

    def get_atomic_forces_list(self):
        return self.atomic_forces_list
    
    def has_force(self):
        if self.atomic_forces_list is not None: 
            return True
        else:
            return False
    def get_force_status(self):
        if self.has_force():
            return "Yes"
        else:
            return "No"

    def get_stress_tensor_list(self):
        return self.stress_tensor_list

    def has_stress(self):
        if self.stress_tensor_list is not None: 
            return True
        else:
            return False

    def get_stress_status(self):
        if self.has_stress():
            return "Yes"
        else:
            return "No"

    def get_mulliken_pop_list(self):
        return self.mulliken_pop_list

    def get_hirshfeld_pop_list(self):
        return self.hirshfeld_pop_list

    def get_dft_plus_u_occ(self):
        return self.dft_plus_u_occ

    def get_geo_opt_info(self):
        return self.geo_opt_info

    def get_geo_opt_info_plot(self, logscale=True):
        plt.rcParams.update(
            {
                'font.size': 20,
                'axes.linewidth': 2,
                'lines.marker': 'o',
                'lines.markeredgecolor': 'black',
                'lines.markeredgewidth': '0.5',
                'lines.markersize': 13,
                'xtick.major.size': 5,
                'xtick.major.width': 2,
                'ytick.major.width': 2
            }
        )
        geo_opt_steps = [one_geo_opt_info["step"]
                         for one_geo_opt_info in self.get_geo_opt_info()[1:]]
        max_step_size = [one_geo_opt_info["max_step_size"]
                         for one_geo_opt_info in self.get_geo_opt_info()[1:]]
        rms_step_size = [one_geo_opt_info["rms_step_size"]
                         for one_geo_opt_info in self.get_geo_opt_info()[1:]]
        max_grad = [one_geo_opt_info["max_gradient"]
                    for one_geo_opt_info in self.get_geo_opt_info()[1:]]
        rms_grad = [one_geo_opt_info["rms_gradient"]
                    for one_geo_opt_info in self.get_geo_opt_info()[1:]]

        fig = plt.figure(figsize=(24, 16), dpi=300)

        gs = GridSpec(2, 2, figure=fig)
        color = 'black'
        ax_max_step = fig.add_subplot(gs[0])
        ax_max_step.plot(geo_opt_steps, max_step_size,
                         color=color, markerfacecolor="#F2F2F2")
        ax_max_step.set_ylabel("Max Step Size")
        ax_max_step.set_xlabel("Optimzation Steps")
        ax_max_step.set_yscale('log')
        ax_max_step.hlines(self.get_geo_opt_info()[-1]["limit_step_size"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
        ax_rms_step = fig.add_subplot(gs[1])
        ax_rms_step.plot(geo_opt_steps, rms_step_size,
                         color=color, markerfacecolor="#C6E070")
        ax_rms_step.set_ylabel("RMS Step Size")
        ax_rms_step.set_xlabel("Optimzation Steps")
        ax_rms_step.set_yscale('log')
        ax_rms_step.hlines(self.get_geo_opt_info()[-1]["limit_rms_step"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
        ax_max_grad = fig.add_subplot(gs[2])
        ax_max_grad.plot(geo_opt_steps, max_grad, color=color,
                         markerfacecolor="#91C46C")
        ax_max_grad.set_xlabel("Optimzation Steps")
        ax_max_grad.set_ylabel("Max Gradient")
        ax_max_grad.set_yscale('log')
        ax_max_grad.hlines(self.get_geo_opt_info()[-1]["limit_gradient"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
        ax_rms_grad = fig.add_subplot(gs[3])
        ax_rms_grad.plot(geo_opt_steps, rms_grad, color=color,
                         markerfacecolor="#5C832F")
        ax_rms_grad.set_ylabel("RMS Gradient")
        ax_rms_grad.set_xlabel("Optimzation Steps")
        ax_rms_grad.set_yscale('log')
        ax_rms_grad.hlines(self.get_geo_opt_info()[-1]["limit_rms_gradient"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
        fig.suptitle("Geometry Optimization Information", fontsize=30)
        fig.tight_layout()
        fig.savefig("geo_opt_info.png")

    def to_ase_atoms(self):
        print("haven't implemented yet")
        pass
