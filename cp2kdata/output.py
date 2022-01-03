import sys
from .block_parser.header_info import parse_header, parse_global, parse_dft
from .block_parser.forces import parse_atomic_forces_list
from .block_parser.mulliken import parse_mulliken_pop_list
from .block_parser.hirshfeld import parse_hirshfeld_pop_list, parse_hirshfeld_pop_list
from .block_parser.dft_plus_u import parse_dft_plus_u_occ
from .block_parser.geo_opt import parse_geo_opt


def check_run_type(run_type):
    implemented_run_type_parsers = ["ENERGY_FORCE", "ENERGY", "MD", "GEO_OPT"]
    if run_type in implemented_run_type_parsers:
        pass
    else:
        raise ValueError


class Cp2kOutput:
    """Class for parsing cp2k output"""

    def __init__(self, output_file) -> None:
        with open(output_file, 'r') as fp:
            self.output_file = "".join(fp.readlines())

        self.header_info = parse_header(self.output_file)
        self.global_info = parse_global(self.output_file)
        self.dft_info = parse_dft(self.output_file)
        try:
            check_run_type(self.global_info["run_type"])
        except ValueError:
            print(
                (
                "Parser for Run Type {0} Haven't Been Implemented Yet!".format(self.global_info["run_type"])
                )
            )
            sys.exit()
        if self.global_info["run_type"] == "GEO_OPT":
            # parse global info
            self.geo_opt_info = parse_geo_opt(self.output_file)
        else:
            self.geo_opt_info = None

        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.mulliken_pop_list = parse_mulliken_pop_list(self.output_file, self.dft_info)
        self.hirshfeld_pop_list = parse_hirshfeld_pop_list(self.output_file)
        self.dft_plus_u_occ = parse_dft_plus_u_occ(self.output_file)

    def get_version_string(self) -> float:
        return self.header_info["version_string"]

    def get_run_type(self) -> float:
        return self.global_info["run_type"]

    def get_atomic_forces_list(self):
        return self.atomic_forces_list

    def get_mulliken_pop_list(self):
        return self.mulliken_pop_list

    def get_hirshfeld_pop_list(self):
        return self.hirshfeld_pop_list

    def get_dft_plus_u_occ(self):
        return self.dft_plus_u_occ
    
    def get_geo_opt_info(self):
        return self.geo_opt_info

    def to_ase_atoms(self):
        pass