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
    'tests/test_energy_force/v6.1/duplicate_header',
    'tests/test_energy_force/v6.1/normal',
    'tests/test_energy_force/v7.1/normal',
    'tests/test_energy_force/v8.1/normal',
    'tests/test_energy_force/v9.0/normal'
]

energy_force_output_list = [
    Cp2kOutput(os.path.join(path, 'output')) for path in energy_force_output_path_list
]


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

    def test_chemical_symbols(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        chemical_symbols = a_test_output.get_chemical_symbols()
        answer = json_to_dict(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "answer.json"
            )
        )
        assert chemical_symbols == answer["chemical_symbols"]

    def test_chemical_symbols_fak(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        chemical_symbols_fake = a_test_output.get_chemical_symbols_fake()
        answer = json_to_dict(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "answer.json"
            )
        )
        assert list(chemical_symbols_fake) == answer["chemical_symbols_fake"]

    def test_atomic_kind(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        atomic_kind = a_test_output.get_atomic_kind()
        answer = json_to_dict(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "answer.json"
            )
        )
        assert list(atomic_kind) == answer["atomic_kind"]

    def test_atomic_kind_list(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        atom_kinds_list = a_test_output.get_atom_kinds_list()
        answer = json_to_dict(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "answer.json"
            )
        )
        assert list(atom_kinds_list) == answer["atom_kinds_list"]

    def test_atom_num(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        atom_num = a_test_output.get_atom_num()
        answer = json_to_dict(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "answer.json"
            )
        )
        assert list(atom_num) == answer["atom_num"]

    def test_init_cell(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        init_cell = a_test_output.get_init_cell()
        answer = np.load(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "init_cell.npy"
            )
        )
        assert np.all(init_cell == answer)     

    def test_init_coordinates(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        init_coord = a_test_output.get_init_atomic_coordinates()
        answer = np.load(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "atomic_init_coord.npy"
            )
        )
        assert np.all(init_coord == answer)

    def test_atomic_forces_list(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        atomic_forces_list = a_test_output.get_atomic_forces_list()
        if a_test_output.has_force():
            answer = np.load(
                os.path.join(
                    output_and_answer_path[1],
                    "answer",
                    "atomic_forces_list.npy"
                )
            )
            assert len(atomic_forces_list) == 1
            assert np.all(atomic_forces_list == answer)
        else:
            assert atomic_forces_list == None

    def test_stress_tensor_list(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        stress_tensor_list = a_test_output.get_stress_tensor_list()

        if a_test_output.has_stress():
            answer = np.load(
                os.path.join(
                    output_and_answer_path[1],
                    "answer",
                    "stress_tensor_list.npy"
                )
            )
            assert len(stress_tensor_list) == 1
            assert np.all(stress_tensor_list == answer)
        else:
            assert stress_tensor_list == None

    def test_pot_energy(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        pot_energy = a_test_output.get_energies_list()
        answer = json_to_dict(
            os.path.join(
                output_and_answer_path[1],
                "answer",
                "answer.json"
            )
        )
        assert len(pot_energy) == 1
        assert list(pot_energy) == answer["pot_energy"]        

#    def test_mulliken_charges(self):
#        pass

#    def test_hirshfeld_charges(self):
#        pass
