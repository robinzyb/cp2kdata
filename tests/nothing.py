from cp2kdata.output import Cp2kOutput
import pytest


test_output_list = [
    Cp2kOutput('tests/v6.1/duplicate_header'),
    Cp2kOutput('tests/v6.1/energy_force'),
    Cp2kOutput('tests/v7.1/energy_force'),
    Cp2kOutput('tests/v7.1/geo_opt'),
    Cp2kOutput('tests/v7.1/aimd'),
    Cp2kOutput('tests/v7.1/dft_plus_u')
]
test_run_type = [
    'ENERGY_FORCE',
    'ENERGY_FORCE',
    'ENERGY_FORCE',
    'GEO_OPT',
    'MD',
    'ENERGY_FORCE'
]

cp2k_ids = ['output({}, {})'.format(c.get_version_string(), c.get_run_type()) for c in test_output_list]

@pytest.fixture(scope='session')
def version_string_avail():
    "Return the existing version"
    return [6.1, 7.1]

# read test case


#@pytest.fixture(params=test_output_list)
#def a_test_output(request):
#    return request.param

@pytest.mark.parametrize('a_test_output', test_output_list)
def test_version_string(a_test_output, version_string_avail):
    cp2k_version = a_test_output.get_version_string()
    assert cp2k_version in version_string_avail


test_param = list(zip(test_output_list, test_run_type))
@pytest.mark.parametrize('a_test_output, a_test_run_type', test_param, ids=cp2k_ids)
def test_run_type(a_test_output, a_test_run_type):
    run_type = a_test_output.get_run_type()
    assert run_type == a_test_run_type

