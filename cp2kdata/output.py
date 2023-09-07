from ast import parse
import sys
import time
import numpy as np
import glob
import os
import sys
from monty.re import regrep
from .plots.geo_opt_plot import geo_opt_info_plot
from .paser_func import *
from .block_parser.header_info import GlobalInfo, Cp2kInfo, DFTInfo


class Cp2kOutput:
    """Class for parsing cp2k output"""

    def __init__(self, output_file=None, run_type: str=None, path_prefix=".", **kwargs):
        # --set some basic information
        self.required_information = kwargs
        self.path_prefix = path_prefix

        if output_file is None:
            self.filename = None
        elif os.path.isfile(os.path.join(self.path_prefix, output_file)):
            self.filename = os.path.join(self.path_prefix, output_file)
        else:
            raise FileNotFoundError(f'cp2k output file {output_file} is not found')

        try:
            self.global_info = self.get_global_info(run_type=run_type, 
                                                   filename=self.filename
                                                   )
        except ValueError as err:
            print(
            "---------------------------------------------\n"
            "Cannot Obtain CP2K RUN_TYPE information.\n"

            "Please check if you have provided an existing cp2k output file.\n"
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


        if self.global_info.print_level == 'LOW':
            raise ValueError("please provide cp2k output file with MEDIUM print level. Print Level Low doesn't provide necessary information for initialize the cp2kdata class.")

        # -- set some basic attribute -- 
        self.num_frames = None
        self.init_atomic_coordinates = None
        self.atomic_kind = None
        self.atom_kind_list = None

        # -- start parse necessary information --

        if self.filename:
            with open(self.filename, 'r') as fp:
                self.output_file = fp.read()
            self.cp2k_info = parse_cp2k_info(self.filename)
            self.DFTInfo = parse_dft_info(self.filename)
        else:
            self.cp2k_info = Cp2kInfo(version="Unknown")
        
        self.check_run_type(run_type=self.global_info.run_type)

        run_type_parser_candidates = {
            "ENERGY_FORCE": self.parse_energy_force,
            "GEO_OPT": self.parse_geo_opt,
            "CELL_OPT": self.parse_cell_opt,
            "MD": self.parse_md
        }

        # call corresponding parser for run types
        parse_run_type = run_type_parser_candidates[self.global_info.run_type]
        parse_run_type()

        #self.errors_info = parse_errors(self.output_file)
        #if ignore_error:
        #    pass
        #else:
        #    if self.errors_info:
        #        if self.errors_info.get("exceed_wall_time", None):
        #            raise ValueError("Your output exceeds wall time, it might be incomplete, if you want to continue, please add set Cp2kOutput(output, ignore_error=True)")


        # elif self.global_info.run_type == "GEO_OPT":
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
        return self.cp2k_info.version

    def get_run_type(self) -> str:
        return self.global_info.run_type

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

    def get_geo_opt_info_plot(self, logscale=True, dst="."):
        try:
            assert self.global_info.run_type == "GEO_OPT"
            geo_opt_info_plot(
                geo_opt_info=self.get_geo_opt_info,
                dst=dst
            )
        except Exception as err:
            print(f"{self.global_info.run_type} can't use this method!")



    def to_ase_atoms(self):
        print("haven't implemented yet")
        pass

    def parse_energy_force(self):
        parser_candidates = {
            "energy": parse_energies_list,
            "forces": parse_atomic_forces_list,
            "stress_tensor": parse_stress_tensor_list,
            "atomic_kinds": parse_atomic_kinds,
            "cells": parse_all_cells
        }
        # convert kwargs to flexible attribute! 
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
        # initial information
        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.atomic_kind = parse_atomic_kinds(self.output_file)


        pos_xyz_file_list = glob.glob(os.path.join(self.path_prefix,"*pos*.xyz"))
        if pos_xyz_file_list:
            self.atomic_frames_list, energies_list_from_pos, self.chemical_symbols = parse_pos_xyz(pos_xyz_file_list[0])
            self.energies_list = energies_list_from_pos

        self.all_cells = parse_all_cells(self.output_file)
        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.stress_tensor_list = parse_stress_tensor_list(self.output_file)

        self.num_frames = len(self.energies_list)

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

            if not hasattr(self, "energies_list"):
                self.energies_list = energies_list_from_pos
        frc_xyz_file_list = glob.glob(os.path.join(self.path_prefix,"*frc*.xyz"))
        if frc_xyz_file_list:
            self.atomic_forces_list = parse_frc_xyz(frc_xyz_file_list[0])

        stress_file_list = glob.glob(os.path.join(self.path_prefix,"*.stress"))
        if stress_file_list:
            self.stress_tensor_list = parse_md_stress(stress_file_list[0])
        else:
            self.stress_tensor_list = None

        self.num_frames = len(self.energies_list)

    @staticmethod
    def get_global_info(run_type=None, filename=None):
        if filename:
            global_info = parse_global_info(filename)
        elif run_type:
            global_info = GlobalInfo(run_type=run_type.upper())
        else:
            raise ValueError("cp2kdata dosen't know your run type!")
        return global_info
    
    @staticmethod
    def check_run_type(run_type):
        implemented_run_type_parsers = \
            ["ENERGY_FORCE", "ENERGY", "MD", "GEO_OPT", "CELL_OPT"]
        if run_type in implemented_run_type_parsers:
            pass
        else:
            raise ValueError(
                f"Parser for Run Type {run_type} Haven't Been Implemented Yet!"
                )
    
        
