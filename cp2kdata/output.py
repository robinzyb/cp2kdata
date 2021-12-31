import sys
from .block_parser.header_info import parse_version_string, parse_run_type
from .block_parser.forces import parse_atomic_forces_list
from .block_parser.mulliken import parse_mulliken_pop_list
from .block_parser.hirshfeld import parse_hirshfeld_pop_list, parse_hirshfeld_pop_list
from .block_parser.dft_plus_u import parse_dft_plus_u_occ


def check_run_type(run_type):
    if run_type == "ENERGY_FORCE":
        pass
    elif run_type == "ENERGY":
        pass
    elif run_type == "MD":
        pass
    else:
        raise ValueError


class Cp2kOutput:
    """Class for parsing cp2k output"""

    def __init__(self, output_file) -> None:
        with open(output_file, 'r') as fp:
            self.output_file = "".join(fp.readlines())

        self.version_string = parse_version_string(self.output_file)
        self.run_type = parse_run_type(self.output_file)
        try:
            check_run_type(self.run_type)
        except ValueError:
            print(
                (
                "Parser for Run Type {0} Haven't Been Implemented Yet!".format(self.run_type)
                )
            )
            sys.exit()
        self.atomic_forces_list = parse_atomic_forces_list(self.output_file)
        self.mulliken_pop_list = parse_mulliken_pop_list(self.output_file)
        self.hirshfeld_pop_list = parse_hirshfeld_pop_list(self.output_file)
        self.dft_plus_u_occ = parse_dft_plus_u_occ(self.output_file)

    def get_version_string(self) -> float:
        return self.version_string

    def get_run_type(self) -> float:
        return self.run_type

    def get_atomic_forces_list(self):
        return self.atomic_forces_list

    def get_mulliken_pop_list(self):
        return self.mulliken_pop_list

    def get_hirshfeld_pop_list(self):
        return self.hirshfeld_pop_list

    def get_dft_plus_u_occ(self):
        return self.dft_plus_u_occ
