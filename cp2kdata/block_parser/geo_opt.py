import regex as re
GEO_OPT_INFO_FIRST_RE = re.compile(
    r"""
    \s+-+\s+Informations\sat\sstep\s=\s+0\s+-+\n
    \s+Optimization\sMethod\s+=\s+\w+\s*\n
    \s+Total\sEnergy\s+=\s+(?P<total_energy>[\s-]\d+\.\d+)\s*\n
    \s+Used\stime\s+=\s+(?P<used_time>[\s-]\d+\.\d+)
    """,
    re.VERBOSE
)

# valid for 7.1
GEO_OPT_INFO_REST_RE = re.compile(
    r"""
    \s+-+\s+Informations\sat\sstep\s=\s+(?P<step>\d+)\s+-+\n
    \s+Optimization\sMethod\s+=\s+\w+\s*\n
    \s+Total\sEnergy\s+=\s+(?P<total_energy>[\s-]\d+\.\d+)\s*\n
    \s+Real\senergy\schange\s+=\s+[\s-]\d+\.\d+\s*\n
    # match once or zero for ?
    (\s+Predicted\schange\sin\senergy\s+=\s+[\s-]\d+\.\d+\s*\n)?
    (\s+Scaling\s+factor\s+=\s+[\s-]\d+\.\d+\s*\n)?
    (\s+Step\s+size\s+=\s+[\s-]\d+\.\d+\s*\n)?
    (\s+Trust\s+radius\s+=\s+[\s-]\d+\.\d+\s*\n)?
    \s+Decrease\sin\senergy\s+=\s+\w+\s*\n
    \s+Used\stime\s+=\s+(?P<used_time>[\s-]\d+\.\d+)\n
    \n
    \s+Convergence\scheck\s:\s*\n
    \s+Max\.\s+step\s+size\s+=\s+(?P<max_step_size>[\s-]\d+\.\d+)\s*\n
    \s+Conv\.\slimit\sfor\sstep\ssize\s+=\s+(?P<limit_step_size>[\s-]\d+\.\d+)\s*\n
    \s+Convergence\sin\sstep\ssize\s+=\s+\w+\s*\n
    \s+RMS\sstep\ssize\s+=\s+(?P<rms_step_size>[\s-]\d+\.\d+)\s*\n
    \s+Conv\.\slimit\sfor\sRMS\sstep\s+=\s+(?P<limit_rms_step>[\s-]\d+\.\d+)\s*\n
    \s+Convergence\sin\sRMS\sstep\s+=\s+\w+\s*\n
    \s+Max\.\sgradient\s+=\s+(?P<max_gradient>[\s-]\d+\.\d+)\s*\n
    \s+Conv\.\slimit\sfor\sgradients\s+=\s+(?P<limit_gradient>[\s-]\d+\.\d+)\s*\n
    (
        \s+Conv\.\sfor\sgradients # two pattern in context ..
        | \s+Conv\.\sin\sgradients
    )
    \s+=\s+\w+\s*\n
    \s+RMS\sgradient\s+=\s+(?P<rms_gradient>[\s-]\d+\.\d+)\s*\n
    \s+Conv\.\slimit\sfor\sRMS\sgrad\.\s+=\s+(?P<limit_rms_gradient>[\s-]\d+\.\d+)\s*\n
    (
        \s+Conv\.\sfor\sgradients # two pattern in context ..
        | \s+Conv\.\sin\sRMS\sgradients
    )
    \s+=\s+\w+\s*\n
    """,
    re.VERBOSE
)


def parse_geo_opt_info(output_file) -> float:
    geo_opt_info = []

    for match in GEO_OPT_INFO_FIRST_RE.finditer(output_file):
        geo_opt_info.append(
            {
                "step": 0,
                "total_energy": float(match["total_energy"]),
                "used_time": float(match["used_time"])
            }
        )
    for match in GEO_OPT_INFO_REST_RE.finditer(output_file):

        geo_opt_info.append(
            {
                "step": int(match["step"]),
                "total_energy": float(match["total_energy"]),
                "used_time": float(match["used_time"]),
                "max_step_size": float(match["max_step_size"]),
                "limit_step_size": float(match["limit_step_size"]),
                "rms_step_size": float(match["rms_step_size"]),
                "limit_rms_step": float(match["limit_rms_step"]),
                "max_gradient": float(match["max_gradient"]),
                "limit_gradient": float(match["limit_gradient"]),
                "rms_gradient": float(match["rms_gradient"]),
                "limit_rms_gradient": float(match["limit_rms_gradient"])
            }
        )
    if geo_opt_info:
        return geo_opt_info
    else:
        return None
