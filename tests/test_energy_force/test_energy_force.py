from cp2kdata.output import Cp2kOutput
import os
import json
import pytest
import numpy as np


def json_to_dict(json_file):
    with open(json_file, "r") as fp:
        dict_content = json.load(fp)
    return dict_content


energy_force_output_path_list = [
    'tests/test_energy_force/v7.1/normal'
    #    'tests/test_energy_force/v6.1/normal'
]

energy_force_output_list = [
    Cp2kOutput(os.path.join(path, 'output')) for path in energy_force_output_path_list
]

# answer_list = [
#    json_to_dict(os.path.join(path, 'answer.json')) for path in energy_force_output_path_list
# ]

test_params = list(zip(energy_force_output_list,
                   energy_force_output_path_list))


@pytest.fixture(params=test_params, scope='class')
def output_and_answer_path(request):
    return request.param


class TestEnergyForce():
    def test_run_type(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        run_type = a_test_output.get_run_type()
        assert run_type == 'ENERGY_FORCE'

    def test_atomic_symbol(self, output_and_answer_path):
        pass
    
    def test_atomic_kind(self):
        pass

    def test_init_coordinates(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        init_coord = a_test_output.get_init_atomic_coordinates()
        answer = np.load(
            os.path.join(
                output_and_answer_path[1], 
                "atomic_init_coord.npy"
                )
            )
        assert np.all(init_coord == answer)
    
    def test_atomic_forces_list(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        atomic_forces_list = a_test_output.get_atomic_forces_list()
        answer = np.load(
            os.path.join(
                output_and_answer_path[1], 
                "atomic_forces_list.npy"
                )
            )
        assert len(atomic_forces_list) == 1
        assert np.all(atomic_forces_list == answer)

    def test_mulliken_charges(self):
        pass

    def test_hirshfeld_charges(self):
        pass
