import regex as re
import numpy as np

VIB_FREQ_RE = re.compile(
    r"""
    \sVIB\|Frequency\s\(cm\^-1\)(\s{0,15}(?P<vib_freq>[\s-]\d+\.\d+)){1,3}
    """,
    re.VERBOSE
)


def parse_vibration_freq_list(output_file):

    vib_freq_list = []
    for match in VIB_FREQ_RE.finditer(output_file):
        #vib_freq_list.append(match["energy"])
        for vib_freq in match.captures('vib_freq'):
            vib_freq_list.append(vib_freq)

    if vib_freq_list:
        return np.array(vib_freq_list, dtype=float)
    else:
        return None