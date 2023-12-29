import regex as re
from dataclasses import dataclass
from monty.re import regrep


@dataclass
class ConvergeInfo:
    converge: bool = False


CONVERGE_PATTERN = \
    r"""(?xm)
    ^\s{1,2}\*\*\*\sSCF\srun\sconverged\sin
    """


def parse_e_f_converge(filename) -> ConvergeInfo:

    info_dict = regrep(
        filename=filename,
        reverse=True,
        patterns={"converge": CONVERGE_PATTERN},
        terminate_on_match=True
    )

    if info_dict['converge']:
        converge_info = ConvergeInfo(converge=True)
    else:
        converge_info = ConvergeInfo(converge=False)
    return converge_info


def parse_md_converge(filename):

    info_dict = regrep(
        filename=filename,
        reverse=True,
        patterns={"converge": CONVERGE_PATTERN},
        terminate_on_match=False
    )
    # print(info_dict['converge'])

# if __name__ == "__main__":
#     file_name = "e_f"
#     converge = parse_e_f_converge(file_name)
#     print(converge)
#     file_name = "output"
#     converge = parse_md_converge(file_name)
#     #print(converge.converge)
