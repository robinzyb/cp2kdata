from ast import parse
import sys

import matplotlib.pyplot as plt
import time
import numpy as np
import glob
import os 
import sys
from monty.re import regrep
from matplotlib.gridspec import GridSpec
from .paser_func import *
from .block_parser.header_info import GlobalInfo, Cp2kInfo, DFTInfo



def get_run_type(run_type, filename):
    if filename:
        ginfo = parse_global_info(filename)
    elif run_type:
        ginfo = GlobalInfo(run_type=run_type.upper())
    else:
        raise ValueError
    return ginfo

def check_run_type(run_type):
    implemented_run_type_parsers = \
        ["ENERGY_FORCE", "ENERGY", "MD", "GEO_OPT", "CELL_OPT"]
    if run_type in implemented_run_type_parsers:
        pass
    else:
        raise ValueError(
            f"Parser for Run Type {run_type} Haven't Been Implemented Yet!"
            )


class Cp2kOutput:
    """Class for parsing cp2k output"""

    def __init__(self, output_file=None, run_type: str=None, path_prefix="."):

        self.path_prefix = path_prefix

        if output_file is None:
            self.filename = None
        elif os.path.isfile(os.path.join(self.path_prefix, output_file)):
            self.filename = os.path.join(self.path_prefix, output_file)
        else:
            self.filename = None

        try:
            self.GlobalInfo = get_run_type(run_type, self.filename)
        except ValueError as err:
            print(
            "---------------------------------------------\n"
            "Cannot Obtain CP2K RUN_TYPE information.\n"
            "Please check if you have provided a existing cp2k output file.\n"
            "If not, you can manually set RUN_TYPE through run_type argument\n" 
            "for md calculation.\n"
            "Example:\n"
                "Cp2kOutput(run_type='MD')\n"
            "Currently, mannual setup of run_type only supports 'MD'.\n"
            "Other run_types, such as 'ENERGY_FORCE', \n"
            "require output file as well.\n"
            "\n"
            " Σ(っ °Д °;)っ \n"
            "\n"
            "---------------------------------------------\n"
            )
            sys.exit()

        # -- set some basic attribute -- 
        self.num_frames = None
        self.init_atomic_coordinates = None
        self.atomic_kind = None
        self.atom_kind_list = None

        # -- start parse necessary information -- 

        if self.filename:
            with open(self.filename, 'r') as fp:
                self.output_file = fp.read()
            self.Cp2kInfo = parse_cp2k_info(self.filename)
            self.DFTInfo = parse_dft_info(self.filename)
        else:
            self.Cp2kInfo = Cp2kInfo(version="Unknown")

        
        check_run_type(self.GlobalInfo.run_type)
        

        Parse_Run_Type = {
            "ENERGY_FORCE": self.parse_energy_force,
            "GEO_OPT": self.parse_geo_opt,
            "CELL_OPT": self.parse_cell_opt,
            "MD": self.parse_md
        }

        # call respective parser for run types
        Parse_Run_Type[self.GlobalInfo.run_type]()
        #self.errors_info = parse_errors(self.output_file)
        #if ignore_error:
        #    pass
        #else:
        #    if self.errors_info:
        #        if self.errors_info.get("exceed_wall_time", None):
        #            raise ValueError("Your output exceeds wall time, it might be incomplete, if you want to continue, please add set Cp2kOutput(output, ignore_error=True)")
        

        # elif self.GlobalInfo.run_type == "GEO_OPT":
        #     # parse global info

        #     self.geo_opt_info = parse_geo_opt(self.output_file)
        #     self.num_frames = len(self.geo_opt_info)
        # else:
        #     self.geo_opt_info = None
        #     self.num_frames = 1

        # self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
        #     self.output_file)

        # self.mulliken_pop_list = parse_mulliken_pop_list(
        #     self.output_file, self.DFTInfo)
        # self.hirshfeld_pop_list = parse_hirshfeld_pop_list(self.output_file)
        # self.dft_plus_u_occ = parse_dft_plus_u_occ(self.output_file)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        txt = "\n"
        txt += "Cp2k Output Summary\n"
        txt += "\n"
        txt += "--------------------------------------\n"
        txt += "\n"
        txt += "Cp2k Version       : {0:s}\n".format(self.get_version_string())
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

    def get_version_string(self) -> str:
        return self.Cp2kInfo.version

    def get_run_type(self) -> str:
        return self.GlobalInfo.run_type

    def get_init_cell(self):
        return self.all_cells[0]

    def get_all_cells(self):
        return self.all_cells

    def get_energies_list(self):
        return self.energies_list

    def get_atomic_kind(self):
        if self.atomic_kind is None:
            return ["Unknown"]
        else:
            return self.atomic_kind
    
    def get_atom_num(self):
        # kind idx is arrange from low to high
        if self.atom_kind_list is None:
            return ["Unknown"]
        else:
            kind_idx, counts = np.unique(
                self.get_atom_kinds_list(), 
                return_counts=True
                )
            return counts

    def get_atom_kinds_list(self):
        if self.atom_kind_list is None:
            return "Unknown"
        else:
            return self.atom_kind_list
            
    def get_chemical_symbols(self):
        return self.chemical_symbols

    def get_chemical_symbols_fake(self):
        if (self.atom_kind_list is not None) and (self.atomic_kind is not None):
            return self.atomic_kind[self.atom_kind_list-1]
        else: 
            return "Unknown"

    def get_init_atomic_coordinates(self):
        if self.init_atomic_coordinates is None:
            return "Unknown"
        else:
            return self.init_atomic_coordinates

    def get_num_atoms(self):
        return len(self.chemical_symbols)

    def get_num_frames(self):
        if self.num_frames is None:
            return "Unknown"           
        else:
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

    def parse_energy_force(self):
        self.geo_opt_info = None
        self.num_frames = 1
        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.all_cells = parse_all_cells(self.output_file)
        self.energies_list = parse_energies_list(self.output_file)

        self.atomic_kind = parse_atomic_kinds(self.output_file)
        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.stress_tensor_list = parse_stress_tensor_list(self.output_file)

    def parse_geo_opt(self):
        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.geo_opt_info = parse_geo_opt(self.output_file)
        self.num_frames = len(self.geo_opt_info)

    def parse_cell_opt(self):
        pass

    def parse_md(self):

        if self.filename:
            self.all_cells = parse_all_cells(self.output_file)
            print(f"You are reading cell information from {self.filename}")
            self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
            self.atomic_kind = parse_atomic_kinds(self.output_file)

        ener_file_list = glob.glob(os.path.join(self.path_prefix, "*.ener"))
        if ener_file_list:
            self.energies_list = parse_md_ener(ener_file_list[0])
        
        pos_xyz_file_list = glob.glob(os.path.join(self.path_prefix,"*pos*.xyz"))
        if pos_xyz_file_list:
            self.atomic_frames_list, energies_list_from_pos, self.chemical_symbols = parse_pos_xyz(pos_xyz_file_list[0])
        
        frc_xyz_file_list = glob.glob(os.path.join(self.path_prefix,"*frc*.xyz"))
        if frc_xyz_file_list:
            self.atomic_forces_list = parse_frc_xyz(frc_xyz_file_list[0])
        
        stress_file_list = glob.glob(os.path.join(self.path_prefix,"*.stress"))
        if stress_file_list:
            self.stress_tensor_list = parse_md_stress(stress_file_list[0])
        else:
            self.stress_tensor_list = None
        
        self.num_frames = len(self.energies_list)
        

