import regex as re
VERSION_STRING_RE = re.compile(
    """
    \sCP2K\|\sversion\sstring:\s+CP2K\sversion\s(?P<version_string>\S+)\n
    """,
    re.VERBOSE
)
def parse_version_string(output_file) -> float:
    version_string = None
    for match in VERSION_STRING_RE.finditer(output_file):
        version_string = match["version_string"]

    if version_string:
        return float(version_string)
    else:
        return None

RUN_TYPE_RE = re.compile(
    """
    \sGLOBAL\|\sRun\stype\s+(?P<run_type>\S+)\n
    """,
    re.VERBOSE
)

def parse_run_type(output_file) -> float:
    run_type = None
    for match in RUN_TYPE_RE.finditer(output_file):
        run_type = match["run_type"]

    if run_type:
        return str(run_type)
    else:
        return None