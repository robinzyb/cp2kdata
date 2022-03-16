from cp2kdata.pdos import pdos_name_parser
import pytest

pdos_file_list = [
    "SFO-3.000-pdos.dat-ALPHA_k1-1.pdos",
    "Hematite-ALPHA_k1-1_21.pdos",
    "Hematite-BETA_k1-1_21.pdos",
    "Hematite-ALPHA_k50-1_21.pdos",
    "Hematite-ALPHA_list5-1_0.pdos",
    "Universality-k3-1_34.pdos"
]

test_answer = [
    {
        "project_name": "SFO-3.000-pdos.dat",
        "spin": "ALPHA",
        "listidx": None,
        "kind": "1",
        "step": None
    },
    {
        "project_name": "Hematite",
        "spin": "ALPHA",
        "listidx": None,
        "kind": "1",
        "step": "21"
    },
    {
        "project_name": "Hematite",
        "spin": "BETA",
        "listidx": None,
        "kind": "1",
        "step": "21"
    },
    {
        "project_name": "Hematite",
        "spin": "ALPHA",
        "listidx": None,
        "kind": "50",
        "step": "21"
    },
    {
        "project_name": "Hematite",
        "spin": "ALPHA",
        "listidx": "5",
        "kind": None,
        "step": "0"
    },
    {
        "project_name": "Universality",
        "spin": None,
        "listidx": None,
        "kind": "3",
        "step": "34"
    }
]

parsed_values = [pdos_name_parser(pdos_file) for pdos_file in pdos_file_list]

test_params = list(zip(parsed_values, test_answer))

@pytest.fixture(params=test_params, scope='class')
def output_and_answer(request):
    return request.param

class TestNameParser():
    def test_project_name(self, output_and_answer):
        assert output_and_answer[0][0] == output_and_answer[1]["project_name"]

    def test_spin(self, output_and_answer):
        assert output_and_answer[0][1] == output_and_answer[1]["spin"]
    
    def test_listidx(self, output_and_answer):
        assert output_and_answer[0][2] == output_and_answer[1]["listidx"]

    def test_kind(self, output_and_answer):
        assert output_and_answer[0][3] == output_and_answer[1]["kind"]

    def test_step(self, output_and_answer):
        assert output_and_answer[0][4] == output_and_answer[1]["step"]


