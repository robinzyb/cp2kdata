from cp2kdata.output import Cp2kOutput
import pytest


@pytest.mark.parametrize(
    'cp2kout',
    [
        Cp2kOutput('v7.1/output_energy_force'),
        Cp2kOutput('v7.1/output_geo_opt'),
        Cp2kOutput('v7.1/output_aimd'),
        Cp2kOutput('v7.1/output_dft_plus_u'),
        Cp2kOutput('v6.1/output_energy_force')
    ]
)
def test_version_string(cp2kout):
    cp2k_version = cp2kout.get_version_string()
    assert cp2k_version