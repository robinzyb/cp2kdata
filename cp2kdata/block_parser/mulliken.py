import regex as re
import numpy as np

MULLIKEN_UKS_RE = re.compile(
    r"""
    \s{21}Mulliken\sPopulation\sAnalysis\s{1}
    \n
    \s\#\s{2}Atom\s{2}Element\s{2}Kind\s{2}Atomic\spopulation\s\(alpha,beta\)\sNet\scharge\s{2}Spin\smoment\n
    (
        \s{,7}(?P<atom>\d+)
        \s+(?P<element>\w+)
        \s+(?P<kind>\d+)
        \s+(?P<alpha>[\s-]\d+\.\d+)
        \s+(?P<beta>[\s-]\d+\.\d+)
        \s+(?P<net_charge>[\s-]\d+\.\d+)
        \s+(?P<spin_moment>[\s-]\d+\.\d+)
        \n
    )+
    """,
    re.VERBOSE
)
MULLIKEN_RKS_RE = re.compile(
    r"""
    \s+Mulliken\sPopulation\sAnalysis\s*\n
    \n
    \s\#.+\n
    (
        \s+(?P<atom>\d+)
        \s+(?P<element>\w+)
        \s+(?P<kind>\d+)
        \s+(?P<alpha>[\s-]\d+\.\d+)
        \s+(?P<net_charge>[\s-]\d+\.\d+)

    )+
    """,
    re.VERBOSE
)


def parse_mulliken_pop_list(output_file, DFTInfo):
    mulliken_pop_list = []
    if DFTInfo.ks_type == 'UKS':
        for match in MULLIKEN_UKS_RE.finditer(output_file):
            # print(match)
            mulliken_pop = []
            for element, alpha, beta, net_charge, spin_moment in zip(*match.captures("element", "alpha", "beta", "net_charge", "spin_moment")):
                # print(match.captures("element", "alpha", "beta", "net_charge", "spin_moment"))
                mulliken_pop.append(
                    {
                        "element": element,
                        "alpha": float(alpha),
                        "beta": float(beta),
                        "net_charge": float(net_charge),
                        "spin_moment": float(spin_moment)
                    }
                )
            mulliken_pop_list.append(mulliken_pop)
    elif DFTInfo.ks_type == "RKS":
        raise NotImplementedError(
            "RKS Mulliken population analysis not implemented")
        for match in MULLIKEN_RKS_RE.finditer(output_file):
            mulliken_pop = []
            for element, alpha, net_charge in zip(*match.captures("element", "alpha", "net_charge")):
                mulliken_pop.append(
                    {
                        "element": element,
                        "alpha": float(alpha),
                        "net_charge": float(net_charge),
                    }
                )
            mulliken_pop_list.append(mulliken_pop)

    if mulliken_pop_list:
        return mulliken_pop_list
    else:
        return None
