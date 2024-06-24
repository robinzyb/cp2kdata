from cp2kdata.output import Cp2kOutput
import os
import json
import pytest
import numpy as np


def json_to_dict(json_file):
    with open(json_file, "r") as fp:
        dict_content = json.load(fp)
    return dict_content


vibrational_analysis_output_path_list = [
    'tests/test_vibrational_analysis/v7.1/normal',

]

vibrational_analysis_output_list = [
    Cp2kOutput(os.path.join(path, 'output')) for path in vibrational_analysis_output_path_list
]


test_params = list(zip(vibrational_analysis_output_list,
                   vibrational_analysis_output_path_list))


@pytest.fixture(params=test_params, scope='class', ids=vibrational_analysis_output_path_list)
def output_and_answer_path(request):
    return request.param

# @pytest.fixture
# def answer_in_dict(output_and_answer_path):
#     answer = json_to_dict(
#             os.path.join(
#                 output_and_answer_path[1],
#                 "answer",
#                 "answer.json"
#             )
#         )
#     return answer

class TestEnergyForce():
    def test_run_type(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        run_type = a_test_output.get_run_type()
        assert run_type == 'VIBRATIONAL_ANALYSIS'

    def test_atomic_forces_list(self, output_and_answer_path):
        a_test_output = output_and_answer_path[0]
        vib_freq = a_test_output.get_vib_freq_list()
        if a_test_output.has_force():
            answer = np.load(
                os.path.join(
                    output_and_answer_path[1],
                    "answer",
                    "vib_freq.npy"
                )
            )
            assert np.all(vib_freq == answer)

