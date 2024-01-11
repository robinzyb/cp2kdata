import regex as re
import numpy as np

HIRSHFELD_RE = re.compile(
    """
    \s+Hirshfeld\sCharges\s*\n
    \n
    \s\#.+\n
    (
        \s+(?P<atom>\d+)
        \s+(?P<element>\w+)
        \s+(?P<kind>\d+)
        \s+(?P<ref_charge>[\s-]\d+\.\d+)
        \s+(?P<alpha>[\s-]\d+\.\d+)
        \s+(?P<beta>[\s-]\d+\.\d+)
        \s+(?P<spin_moment>[\s-]\d+\.\d+)
        \s+(?P<net_charge>[\s-]\d+\.\d+)
        \n
    )+
    """,
    re.VERBOSE
)


def parse_hirshfeld_pop_list(output_file):
    hirshfeld_pop_list = []
    for match in HIRSHFELD_RE.finditer(output_file):
        hirshfeld_pop = []
        for element, alpha, beta, net_charge, spin_moment in zip(*match.captures("element", "alpha", "beta", "net_charge", "spin_moment")):
            hirshfeld_pop.append(
                {
                    "element": element,
                    "alpha": float(alpha),
                    "beta": float(beta),
                    "net_charge": float(net_charge),
                    "spin_moment": float(spin_moment)
                }
            )
        hirshfeld_pop_list.append(hirshfeld_pop)
    if hirshfeld_pop_list:
        return hirshfeld_pop_list[:-1]
    else:
        return None
