from cp2kdata.output import Cp2kOutput
import pytest


@pytest.fixture(scope='session')
def version_string_avail():
    "Return the existing version"
    return [6.1, 7.1]

test_output_list = [
    Cp2kOutput('v6.1/duplicate_header'),
    Cp2kOutput('v6.1/energy_force'),
    Cp2kOutput('v7.1/energy_force'),
    Cp2kOutput('v7.1/geo_opt'),
    Cp2kOutput('v7.1/aimd'),
    Cp2kOutput('v7.1/dft_plus_u')
    
]

# read test case
@pytest.fixture(params=test_output_list)
def a_test_output(request):
    return request.param


def test_version_string(a_test_output, version_string_avail):
    cp2k_version = a_test_output.get_version_string()
    assert cp2k_version in version_string_avail
