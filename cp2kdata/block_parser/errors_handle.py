import regex as re
EXCEED_WALL_TIME_RE = re.compile(
    r"""
    \sexceeded\srequested\sexecution\stime
    """,
    re.VERBOSE
)


def parse_errors(output_file):
    errors_info = {}

    for match in EXCEED_WALL_TIME_RE.finditer(output_file):
        # print(match)
        if match:
            errors_info = {
                "exceed_wall_time": True
            }

    if errors_info:
        return errors_info
    else:
        return None
