import numpy as np
import pytest
import dpdata
import os

e_f_output_path_list = [
    "tests/test_dpdata/v7.1/e_f_no_converge"
]

e_f_dpdata_list = [
   dpdata.LabeledSystem(
        file_name = os.path.join(path, "output"), 
        fmt="cp2kdata/e_f"
        ) for path in e_f_output_path_list
]

@pytest.fixture(params=e_f_dpdata_list, scope='class', ids=e_f_output_path_list)
def cp2k_and_ref(request):
    return request.param

class TestLabeledSysNoCon():
    # test for Non converged output

    def test_atom_numbs(self, cp2k_and_ref):
        assert cp2k_and_ref.data['atom_numbs'] == []

    def test_atom_names(self, cp2k_and_ref):
        assert cp2k_and_ref.data['atom_names'] == []

    def test_atom_types(self, cp2k_and_ref):
        assert cp2k_and_ref.data['atom_types'] == []

    def test_cell(self, cp2k_and_ref):
        assert cp2k_and_ref.data['cells'] == []

    def test_coord(self, cp2k_and_ref): 
        assert cp2k_and_ref.data['coords'] == []

    def test_energy(self, cp2k_and_ref):
        assert cp2k_and_ref.data['energies'] == []

    def test_force(self, cp2k_and_ref):
        assert cp2k_and_ref.data['forces'] == []

    def test_virial(self, cp2k_and_ref):
        # test if the keyerror throw right message
        with pytest.raises(KeyError) as excinfo:
            cp2k_and_ref.data['virials']
        exception_msg = excinfo.value.args[0]
        assert exception_msg == 'virials'