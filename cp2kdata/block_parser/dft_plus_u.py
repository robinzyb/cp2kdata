import regex as re
import numpy as np

PLUS_U_RE = re.compile(
    """
    \sDFT\+U\soccupations\sof\sspin\s(?P<spin>\d)
    \sfor\sthe\satoms\sof\satomic\skind\s(?P<kind>\d+):\s\w+\s*\n
    \n
    \s+Atom\s+Shell(\s+\w[\+-\d]*)+\s+Trace\n
    (
    \s+(?P<atom>\d+)\s+(?P<shell_1>\d+)(\s+\d+\.\d+)+\n
    \s+(?P<atom>\d+)\s+(?P<shell_2>\d+)(\s+\d+\.\d+)+\n
    \s+Total(\s+\d+\.\d+)+\n
    )+
    """,
    re.VERBOSE
)
#    (
#        \s+(?P<atom>\d+)
#        \s+(?P<element>\w+)
#        \s+(?P<kind>\d+)
#        \s+(?P<alpha>[\s-]\d+\.\d+)
#        \s+(?P<beta>[\s-]\d+\.\d+)
#        \s+(?P<net_charge>[\s-]\d+\.\d+)
#        \s+(?P<spin_moment>[\s-]\d+\.\d+)
#        \n
#    )+


def parse_dft_plus_u_occ(output_file):
    dft_plus_u_occ = []
    for match in PLUS_U_RE.finditer(output_file):
        pass
#        print(match)
#        for element, alpha, beta, net_charge, spin_moment in zip(*match.captures("element", "alpha", "beta", "net_charge", "spin_moment")):
#            dft_plus_u_occ.append(
#                {
#                    "element": element,
#                    "alpha": float(alpha),
#                    "beta": float(beta),
#                    "net_charge": float(net_charge),
#                    "spin_moment": float(spin_moment)
#                }
#            )
    if dft_plus_u_occ:
        return dft_plus_u_occ
    else:
        return None
