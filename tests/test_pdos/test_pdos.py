from pathlib import Path
import json
import pytest
import numpy as np
from cp2kdata import Cp2kPdos


def json_to_dict(json_file):
    with open(json_file, "r") as fp:
        dict_content = json.load(fp)
    return dict_content

PYTEST_FIXTURES_PATH = Path("tests/test_pdos/pdos_files")
pdos_file_list = [
    "case_1_pdos/bivo4-water-k1-1_0.pdos"
]

cp2kpdos_list = [ Cp2kPdos(PYTEST_FIXTURES_PATH/file) for file in pdos_file_list ]
cp2kpdos_ref_list = [ 
    PYTEST_FIXTURES_PATH/Path(file).parent for file in pdos_file_list 
    ]

test_cases = list(zip(cp2kpdos_list, cp2kpdos_ref_list))

@pytest.fixture(params=test_cases, scope='class', ids=pdos_file_list)
def output_and_answer(request):
    return request.param

@pytest.fixture
def answer_in_dict(output_and_answer):
    return json_to_dict(output_and_answer[1]/"answer"/"answer.json")

class TestCp2kPdos:
    
    def test_project_name(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].project_name == answer_in_dict["project_name"]
    
    def test_spin(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].spin == answer_in_dict["spin"]
    
    def test_listidx(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].listidx == answer_in_dict["listidx"]
    
    def test_kind(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].kind == answer_in_dict["kind"]
    
    def test_timestep(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].timestep == answer_in_dict["timestep"]
    
    def test_fermi(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].fermi == answer_in_dict["fermi"]
    
    def test_homo_ener(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].get_homo_ener() == answer_in_dict["homo_ener"]

    def test_lumo_ener(self, output_and_answer, answer_in_dict):
        assert output_and_answer[0].get_lumo_ener() == answer_in_dict["lumo_ener"]

    def test_occupation(self, output_and_answer):
        answer = np.load(output_and_answer[1]/"answer"/"occupation.npy")
        np.testing.assert_almost_equal(output_and_answer[0].occupation,
                                       answer,
                                       decimal = 6,
                                       err_msg = 'occupation failed')
        
    def test_get_dos(self, output_and_answer):
        answer = np.load(output_and_answer[1]/"answer"/"dos.npy")
        np.testing.assert_almost_equal(output_and_answer[0].get_dos(),
                                       answer,
                                       decimal = 6,
                                       err_msg = 'dos failed')
    