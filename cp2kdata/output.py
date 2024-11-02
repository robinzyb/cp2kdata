import sys
import numpy as np
import glob
import os
import sys
from functools import cached_property

from cp2kdata.plots.geo_opt_plot import geo_opt_info_plot
from cp2kdata.log import get_logger
from cp2kdata.utils import format_logger
from cp2kdata.block_parser.header_info import GlobalInfo, Cp2kInfo, DFTInfo
from cp2kdata.block_parser.dft_plus_u import parse_dft_plus_u_occ
from cp2kdata.block_parser.forces import parse_atomic_forces_list
from cp2kdata.block_parser.geo_opt import parse_geo_opt_info
from cp2kdata.block_parser.header_info import parse_dft_info, parse_global_info, parse_cp2k_info, parse_md_info
from cp2kdata.block_parser.hirshfeld import parse_hirshfeld_pop_list
from cp2kdata.block_parser.mulliken import parse_mulliken_pop_list
from cp2kdata.block_parser.energies import parse_energies_list
from cp2kdata.block_parser.coordinates import parse_init_atomic_coordinates
from cp2kdata.block_parser.atomic_kind import parse_atomic_kinds
from cp2kdata.block_parser.errors_handle import parse_errors
from cp2kdata.block_parser.stress import parse_stress_tensor_list
from cp2kdata.block_parser.cells import parse_all_cells, parse_all_md_cells
from cp2kdata.block_parser.md_xyz import parse_md_ener, parse_pos_xyz, parse_frc_xyz, parse_md_stress, parse_md_cell
from cp2kdata.block_parser.vibration import parse_vibration_freq_list

logger = get_logger(__name__)

class Cp2kOutput:
    """Class for parsing cp2k output"""

    def __init__(
            self,
            output_file: str = None,
            run_type: str = None,
            path_prefix: str = ".",
            restart: bool = None,
            **kwargs
    ):

        # --set some basic information
        # self.required_information = kwargs
        self.path_prefix = path_prefix

        if output_file is None:
            self.filename = None
        elif os.path.isfile(os.path.join(self.path_prefix, output_file)):
            self.filename = os.path.join(self.path_prefix, output_file)
        else:
            raise FileNotFoundError(
                f'cp2k output file {output_file} is not found')

        try:
            self.global_info = self.get_global_info(run_type=run_type,
                                                    filename=self.filename
                                                    )
        except ValueError as err:
            logger.error(
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
            raise ValueError(
                "please provide cp2k output file with MEDIUM print level. Print Level Low doesn't provide necessary information for initialize the cp2kdata class.")

        # -- set some basic attributes --
        self.num_frames = None
        self.init_atomic_coordinates = None
        self.atomic_kind = None
        self.atom_kind_list = None

        # -- start parse necessary information --
        # sometimes I use self.filename and sometimes I use self.output_file
        # self.filename is used for parsing information by monty package.
        if self.filename:
            with open(self.filename, 'r') as fp:
                self.output_file = fp.read()
            self.cp2k_info = parse_cp2k_info(self.filename)
            self.dft_info = parse_dft_info(self.filename)
        else:
            self.cp2k_info = Cp2kInfo(version="Unknown")

        # overwrite the restart if users provide restart information
        # restart should be true or false
        if restart is not None:
            self.cp2k_info.restart = restart
            logger.debug("Overwrite restart information with user provided restart = True.")

        self.check_run_type(run_type=self.global_info.run_type)

        run_type_parser_candidates = {
            "ENERGY": self.parse_energy_force,
            "ENERGY_FORCE": self.parse_energy_force,
            "GEO_OPT": self.parse_geo_opt,
            "CELL_OPT": self.parse_cell_opt,
            "MD": self.parse_md,
            "VIBRATIONAL_ANALYSIS": self.parse_vibrational_analysis
        }

        # call corresponding parser for run types
        parse_run_type = run_type_parser_candidates.get(
            self.global_info.run_type, None)
        if parse_run_type:
            parse_run_type()
        else:
            f"parser for run type {self.global_info.run_type} is not implemented yet!"

        # self.errors_info = parse_errors(self.output_file)
        # if ignore_error:
        #    pass
        # else:
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

    def get_ase_atoms(self):
        from ase import Atoms
        symbols = self.get_chemical_symbols()
        positions = self.init_atomic_coordinates.copy()
        cell = self.get_init_cell()
        ase_atoms = Atoms(
            symbols=symbols, positions=positions, cell=cell, pbc=True)
        return ase_atoms

    @cached_property
    def mulliken_pop_list(self):
        # use cached property to prase only once
        return parse_mulliken_pop_list(self.output_file, self.dft_info)

    def get_mulliken_pop_list(self):
        return self.mulliken_pop_list

    def get_spin_moment_mulliken_list(self):
        mulliken_pop_list = self.get_mulliken_pop_list()
        spin_moment_mulliken_list = []

        for mulliken_pop in mulliken_pop_list:
            spin_moment_mulliken = np.array(
                [mulliken_atom['spin_moment'] for mulliken_atom in mulliken_pop], dtype=float)
            spin_moment_mulliken_list.append(spin_moment_mulliken)
        spin_moment_mulliken_list = np.array(spin_moment_mulliken_list)

        return spin_moment_mulliken_list

    def get_spin_moment_list(self, type='mulliken'):
        if type == 'mulliken':
            return self.get_spin_moment_mulliken_list()
        else:
            raise NotImplementedError(
                "Only Mulliken Spin Moment is implemented now")

    # def get_hirshfeld_pop_list(self):
    #     return self.hirshfeld_pop_list

    # def get_dft_plus_u_occ(self):
    #     return self.dft_plus_u_occ

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
        self.geo_opt_info = None
        self.num_frames = 1
        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.all_cells = parse_all_cells(self.output_file)
        self.energies_list = parse_energies_list(self.output_file)

        self.atomic_kind = parse_atomic_kinds(self.output_file)
        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.stress_tensor_list = parse_stress_tensor_list(self.output_file)

    def parse_vibrational_analysis(self):
        self.parse_energy_force()

    def parse_geo_opt(self):
        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.geo_opt_info = parse_geo_opt_info(self.output_file)
        self.energies_list = parse_energies_list(self.output_file)
        self.num_frames = len(self.geo_opt_info)
        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.stress_tensor_list = parse_stress_tensor_list(self.output_file)

    def parse_cell_opt(self):
        # initial information
        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.atomic_kind = parse_atomic_kinds(self.output_file)

        pos_xyz_file_list = glob.glob(
            os.path.join(self.path_prefix, "*pos*.xyz"))
        if pos_xyz_file_list:
            self.atomic_frames_list, energies_list_from_pos, self.chemical_symbols = parse_pos_xyz(
                pos_xyz_file_list[0])
            self.energies_list = energies_list_from_pos

        self.all_cells = parse_all_cells(self.output_file)
        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.stress_tensor_list = parse_stress_tensor_list(self.output_file)

        self.num_frames = len(self.energies_list)

    def parse_md(self):
        self.md_info = parse_md_info(self.filename)
        self.check_md_type(md_type=self.md_info.ensemble_type)

        # parse md energies
        ener_file_list = glob.glob(os.path.join(self.path_prefix, "*.ener"))
        if ener_file_list:
            self.energies_list = parse_md_ener(ener_file_list[0])

        # parse md poses
        pos_xyz_file_list = glob.glob(
            os.path.join(self.path_prefix, "*-pos-*.xyz"))

        n_pos_xyz_files = len(pos_xyz_file_list)
        if n_pos_xyz_files > 1:
            raise ValueError(
                f"Cp2kData found {n_pos_xyz_files} pos files.\n"
                f"{pos_xyz_file_list}.\n"
                f"Please remove extra pos files and keep only one pos file in the folder."
                )

        if pos_xyz_file_list:
            # TODO: Is it possible to have no pos file?
            self.atomic_frames_list, energies_list_from_pos, self.chemical_symbols = parse_pos_xyz(
                pos_xyz_file_list[0])

            if not hasattr(self, "energies_list"):
                self.energies_list = energies_list_from_pos
        else:
            # if no pos file and ener file, parse energies from the output file
            if not hasattr(self, "energies_list"):
                format_logger(info="Energies", filename=self.filename)
                self.energies_list = parse_energies_list(self.output_file)
                self.energies_list = self.drop_last_info(
                    self.cp2k_info, self.energies_list)
            self.atomic_frames_list = None

        frc_xyz_file_list = glob.glob(
            os.path.join(self.path_prefix, "*frc*.xyz"))
        if frc_xyz_file_list:
            self.atomic_forces_list = parse_frc_xyz(frc_xyz_file_list[0])
        else:
            format_logger(info="Forces", filename=self.filename)
            self.atomic_forces_list = parse_atomic_forces_list(
                self.output_file)

            self.atomic_forces_list = self.drop_first_info(
                self.cp2k_info, self.atomic_forces_list, info="forces")

            self.atomic_forces_list = self.drop_last_info(
                self.cp2k_info, self.atomic_forces_list, info="forces")

        stress_file_list = glob.glob(
            os.path.join(self.path_prefix, "*.stress"))
        if stress_file_list:
            logger.warning(
                f"cp2kdata found a file recording stresses: {stress_file_list[0]}"
                f"But the parser for {stress_file_list[0]} is not supported yet"
            )
            # TODO: the unit of stress is bar in -1.stress file, but not GPa in the output file
            # TODO: however, covert bar to GPa is not consistent with the output file!
            # TODO: check this latter
            # self.stress_tensor_list = parse_md_stress(stress_file_list[0])
            self.stress_tensor_list = None
        else:
            format_logger(info="Stresses", filename=self.filename)
            self.stress_tensor_list = parse_stress_tensor_list(
                self.output_file)

            # stress tensor could be None if the output file doesn't contain stress information
            if self.stress_tensor_list is not None:
                self.stress_tensor_list = self.drop_first_info(
                    self.cp2k_info, self.stress_tensor_list, info="stresses")

                self.stress_tensor_list = self.drop_last_info(
                    self.cp2k_info, self.stress_tensor_list, info="stresses")

        self.num_frames = len(self.energies_list)

        # here parse cell information
        WARNING_MSG_PARSE_CELL_FROM_OUTPUT = \
            (
                "\n"
                "cp2kdata is parsing md cell information from output file.\n"
                "The raw data of cell information are lengths and angles,\n"
                "which are later transformed to cell matrices by codes.\n"
                "However, the a axis of the cell are always assumed to be aligned to "
                "the x axis of the coordinate.\n"
                "Make sure the a axis in real cell matrices are always aligned to x axis.\n"
                "Otherwise, parsing cell information from `-1.cell` file is recommended.\n"

                "CP2K input setup for write `-1.cell` file\n"
                "------------------\n"
                "&MOTION\n"
                " &PRINT\n"
                "   &CELL\n"
                "     &EACH\n"
                "       MD 1\n"
                "     &END EACH\n"
                "   &END CELL\n"
                " &END PRINT\n"
                "&END MOTION\n"
                "------------------\n"
            )

        cell_file_list = glob.glob(os.path.join(self.path_prefix, "*.cell"))
        if (self.md_info.ensemble_type == "NVT") or \
            (self.md_info.ensemble_type == "NVE") or \
                (self.md_info.ensemble_type == "REFTRAJ"):  # not ture REFTRAJ also contrains different cell?
            if cell_file_list:
                self.all_cells = parse_md_cell(cell_file_list[0])
            elif self.filename:
                format_logger(info="Cells", filename=self.filename)
                logger.warning(WARNING_MSG_PARSE_CELL_FROM_OUTPUT)

                # self.organize_md_cell()
                # parse the first cell
                first_cell = parse_all_cells(self.output_file)
                assert first_cell.shape == (1, 3, 3)
                self.all_cells = first_cell
                self.all_cells = np.repeat(
                    self.all_cells, repeats=self.num_frames, axis=0)

        elif (self.md_info.ensemble_type == "NPT_F"):
            if cell_file_list:
                # all cells include initial cell
                self.all_cells = parse_md_cell(cell_file_list[0])
            elif self.filename:
                format_logger(info="Cells", filename=self.filename)
                logger.warning(WARNING_MSG_PARSE_CELL_FROM_OUTPUT)

                self.organize_md_cell()

        elif (self.md_info.ensemble_type == "NPT_I"):
            if cell_file_list:
                self.all_cells = parse_md_cell(cell_file_list[0])
            elif self.filename:
                format_logger(info="Cells", filename=self.filename)
                logger.warning(WARNING_MSG_PARSE_CELL_FROM_OUTPUT)

                self.organize_md_cell()

        self.init_atomic_coordinates, self.atom_kind_list, self.chemical_symbols = parse_init_atomic_coordinates(
            self.output_file)
        self.atomic_kind = parse_atomic_kinds(self.output_file)

    def organize_md_cell(self):
        # whether reserve the first cell is determined by the restart

        WARNING_MSG = "cp2kdata obtains more than one initial cell from the output file, \
                    please check if your output file has duplicated header information."

        # only parse the first cell
        first_cell = parse_all_cells(self.output_file)
        assert first_cell.shape == (1, 3, 3), WARNING_MSG
        # parse the rest of the cells
        self.all_cells = parse_all_md_cells(self.output_file,
                                            cp2k_info=self.cp2k_info,
                                            init_cell_info=first_cell[0])
        # prepend the first cell
        if self.cp2k_info.restart is not True:
            self.all_cells = np.insert(
                self.all_cells, 0, first_cell[0], axis=0)

    @cached_property
    def vib_freq_list(self):
        assert self.global_info.run_type == "VIBRATIONAL_ANALYSIS", "vibrational frequency is only available for VIBRATIONAL_ANALYSIS run type."
        # use cached property to prase only once
        return parse_vibration_freq_list(self.output_file)

    def get_vib_freq_list(self):
        return self.vib_freq_list

    @staticmethod
    def drop_first_info(cp2k_info, array, info="info"):
        # drop first info parsed from output if it restart from preivous MD run
        if cp2k_info.restart == True:
            logger.info(
                f"The cp2k output is restarted from previous MD run, drop the first {info}."
            )
            array = array[1:]
        return array

    @staticmethod
    def drop_last_info(cp2k_info, array, info="info"):
        # drop last info parsed from output if it is terminated by request (touch EXIT)
        if cp2k_info.terminated_by_request == True:
            print(
                f"The cp2k output is terminated by user request, drop the last {info}.")
            array = array[:-1]
        return array

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
            ["ENERGY_FORCE", "ENERGY", "MD", "GEO_OPT",
                "CELL_OPT", "VIBRATIONAL_ANALYSIS"]
        if run_type not in implemented_run_type_parsers:
            raise ValueError(
                f"Parser for Run Type {run_type} haven't been implemented yet!"
                "Please contact the developer for more information."
            )

    @staticmethod
    def check_md_type(md_type):
        implemented_ensemble_type_parsers = \
            ["NVE", "NVT", "NPT_F", "NPT_I", "REFTRAJ"]
        if md_type not in implemented_ensemble_type_parsers:
            raise ValueError(
                f"Parser for MD Type {md_type} haven't been implemented yet!\n"
                "Please contact the developer for more information."
            )
