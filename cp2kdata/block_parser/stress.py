import regex as re
import numpy as np

STRESS_RE = re.compile(
    r"""
    (\sSTRESS\sTENSOR\s\[GPa\]
    \n
    \s+X\s+Y\s+Z\s*\n
    \s+X
    \s+(?P<xx>[\s-]\d+\.\d+)
    \s+(?P<xy>[\s-]\d+\.\d+)
    \s+(?P<xz>[\s-]\d+\.\d+)\n
    \s+Y
    \s+(?P<yx>[\s-]\d+\.\d+)
    \s+(?P<yy>[\s-]\d+\.\d+)
    \s+(?P<yz>[\s-]\d+\.\d+)\n
    \s+Z
    \s+(?P<zx>[\s-]\d+\.\d+)
    \s+(?P<zy>[\s-]\d+\.\d+)
    \s+(?P<zz>[\s-]\d+\.\d+)\n
    |# or another pattern used in v8.1
    \s+STRESS\|\sAnalytical\sstress\stensor\s\[GPa\]\s*\n
    \s+STRESS\|\s+x\s+y\s+z\s*\n
    \s+STRESS\|\s+x
    \s+(?P<xx>[\s-]\d+\.\d+E[\+\-]\d\d)
    \s+(?P<xy>[\s-]\d+\.\d+E[\+\-]\d\d)
    \s+(?P<xz>[\s-]\d+\.\d+E[\+\-]\d\d)\n
    \s+STRESS\|\s+y
    \s+(?P<yx>[\s-]\d+\.\d+E[\+\-]\d\d)
    \s+(?P<yy>[\s-]\d+\.\d+E[\+\-]\d\d)
    \s+(?P<yz>[\s-]\d+\.\d+E[\+\-]\d\d)\n
    \s+STRESS\|\s+z
    \s+(?P<zx>[\s-]\d+\.\d+E[\+\-]\d\d)
    \s+(?P<zy>[\s-]\d+\.\d+E[\+\-]\d\d)
    \s+(?P<zz>[\s-]\d+\.\d+E[\+\-]\d\d)\n
    )
    """,
    re.VERBOSE
)


def parse_stress_tensor_list(output_file):
    stress_tensor_list = []
    for match in STRESS_RE.finditer(output_file):
        stress_tensor = [
            [match["xx"], match["xy"], match["xz"]],
            [match["yx"], match["yy"], match["yz"]],
            [match["zx"], match["zy"], match["zz"]]
        ]
        stress_tensor_list.append(stress_tensor)
    if stress_tensor_list:
        return np.array(stress_tensor_list, dtype=float)
    else:
        return None
