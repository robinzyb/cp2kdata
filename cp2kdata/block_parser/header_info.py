import regex as re
HEADER_INFO_RE = re.compile(
    r"""
    \s+CP2K\|\sversion\sstring:\s+CP2K\sversion\s(?P<version_string>\S+)\n
    (\s+CP2K\|.+\n)+
    """,
    re.VERBOSE
)

def parse_header(output_file) -> float:
    header_info = {}
    
    for match in HEADER_INFO_RE.finditer(output_file):

        header_info = {
            "version_string": float(match["version_string"])
        }

    if header_info:
        return header_info
    else:
        return None

GLOBAL_INFO_RE = re.compile(
    r"""
    \s+GLOBAL\|\sRun\stype\s+(?P<run_type>\w+)\n
    (\s+GLOBAL\|.+\n)+
    """,
    re.VERBOSE
)

def parse_global(output_file) -> float:
    global_info = {}
    
    for match in GLOBAL_INFO_RE.finditer(output_file):

        global_info = {
            "run_type": match["run_type"]
        }

    if global_info:
        return global_info
    else:
        return None
DFT_INFO_RE = re.compile(
    r"""
    (
        \s+DFT\|\sSpin\srestricted\sKohn-Sham\s\(RKS\)\scalculation\s+(?P<ks_type>\w+)\n
        |
        \s+DFT\|\sSpin\sunrestricted\s\(spin-polarized\)\sKohn-Sham\scalculation\s+(?P<ks_type>\w+)\n
    )
   (\s+DFT\|.+\n)+
    """,
    re.VERBOSE
)

def parse_dft(output_file) -> float:
    dft_info = {}
    
    for match in DFT_INFO_RE.finditer(output_file):
        dft_info = {
            "ks_type": match["ks_type"]
        }

    if dft_info:
        return dft_info
    else:
        return None