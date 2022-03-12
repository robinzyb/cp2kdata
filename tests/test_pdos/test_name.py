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

test_params = list(zip(pdos_file_list, test_answer))

@pytest.fixture(params=test_params, scope='class')
def output_and_answer(request):
    return request.param

class TestNameParser():
    def test_match(self, output_and_answer):
        project_name, spin, listidx, kind, step = pdos_name_parser(output_and_answer[0])
        #print(listidx)
        assert project_name == output_and_answer[1]["project_name"]
        assert spin == output_and_answer[1]["spin"]
        assert listidx == output_and_answer[1]["listidx"]
        assert kind == output_and_answer[1]["kind"]
        assert step == output_and_answer[1]["step"]


