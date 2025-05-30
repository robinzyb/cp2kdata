import numpy as np
import pytest
import json

#from pytest import approx
import dpdata
import os

# write abs path
e_f_output_path_list = [
    "tests/test_dpdata/v6.1/e_f_normal_output",
    "tests/test_dpdata/v7.1/e_f_duplicate_header",
    "tests/test_dpdata/v7.1/e_f_element_replace"
]

aimd_output_path_list = [
    "tests/test_dpdata/v7.1/aimd",
    "tests/test_dpdata/v7.1/aimd_virial",
    "tests/test_dpdata/v7.1/aimd_virial_in_output",
    "tests/test_dpdata/v7.1/aimd_npt_f",
    "tests/test_dpdata/v9.1/xTBmd_npt_i",
    "tests/test_dpdata/v9.1/npt_i",
    "tests/test_dpdata/v2022.1/aimd",
    "tests/test_dpdata/v2022.1/aimd_exit",
    "tests/test_dpdata/v2022.2/aimd_npt_i",
    "tests/test_dpdata/v2023.1/aimd_nvt",
    "tests/test_dpdata/v2023.1/aimd_npt_f",
    "tests/test_dpdata/v2023.2/aimd_nvt_restart",
    "tests/test_dpdata/v2024.1/aimd_npt_i_restart",
    "tests/test_dpdata/v_undefined/aimd_nvt_no_output",
]

e_f_dpdata_list = [
   dpdata.LabeledSystem(
        file_name = os.path.join(path, "output"),
        fmt="cp2kdata/e_f"
        ) for path in e_f_output_path_list
]

e_f_dpdata_ref_list = [
    dpdata.LabeledSystem(
        file_name = os.path.join(path, "deepmd"),
        fmt="deepmd/npy"
        ) for path in e_f_output_path_list
]


# Test cases for AIMD are complicated. Sometimes they don't have output files
aimd_dpdata_list = []

for path in aimd_output_path_list:
    if os.path.exists(os.path.join(path, "output")):
        aimd_dpdata_list.append(
            dpdata.LabeledSystem(
                file_name = path,
                cp2k_output_name="output",
                fmt="cp2kdata/md",
            )
       )
    # if no ouput file is found, we will find some parameter from the dpdata_input_param.json
    else:
        dpdata_input_param_path = os.path.join(path, "dpdata_input_param.json")
        with open(dpdata_input_param_path, "r") as f:
            dpdata_param = json.load(f)
        cells = dpdata_param.get("cells", None)
        cells = np.array(cells)
        ensemble_type = dpdata_param.get("ensemble_type", None)
        aimd_dpdata_list.append(
            dpdata.LabeledSystem(
                file_name = path,
                cp2k_output_name=None,
                cells = cells,
                ensemble_type = ensemble_type,
                fmt="cp2kdata/md",
            )
        )



aimd_dpdata_ref_list = [
    dpdata.LabeledSystem(
        file_name = os.path.join(path, "deepmd"),
        fmt="deepmd/npy"
        ) for path in aimd_output_path_list
]

# zip the test cases and its reference.
test_params = list(
    zip(
        e_f_dpdata_list + aimd_dpdata_list,
        e_f_dpdata_ref_list + aimd_dpdata_ref_list
        )
    )

# test case
@pytest.fixture(params=test_params, scope='class', ids=e_f_output_path_list+aimd_output_path_list)
def cp2k_and_ref(request):
    return request.param

#@pytest.mark.parametrize(id=(e_f_output_path_list+aimd_output_path_list))
class TestLabeledSys():
    def test_len_func(self, cp2k_and_ref):
        assert len(cp2k_and_ref[0]) == len(cp2k_and_ref[1])

    def test_add_func(self, cp2k_and_ref):
        assert len(cp2k_and_ref[0]+cp2k_and_ref[0]) == len(cp2k_and_ref[1]+cp2k_and_ref[1])

    def test_atom_numbs(self, cp2k_and_ref):
        assert cp2k_and_ref[0].data['atom_numbs'] == cp2k_and_ref[1].data['atom_numbs']

    def test_atom_names(self, cp2k_and_ref):
        assert cp2k_and_ref[0].data['atom_names'] == cp2k_and_ref[1].data['atom_names']

    def test_atom_types(self, cp2k_and_ref):
        np.testing.assert_equal(
            cp2k_and_ref[0].data['atom_types'],
            cp2k_and_ref[1].data['atom_types']
            )

    def test_orig(self, cp2k_and_ref):
        for d0 in range(3) :
            assert cp2k_and_ref[0].data['orig'][d0] == cp2k_and_ref[1].data['orig'][d0]

    def test_nframes(self, cp2k_and_ref):
        assert cp2k_and_ref[0].get_nframes() == cp2k_and_ref[1].get_nframes()

    def test_cell(self, cp2k_and_ref):
        assert cp2k_and_ref[0].get_nframes() == cp2k_and_ref[1].get_nframes()
        if not cp2k_and_ref[0].nopbc and not cp2k_and_ref[1].nopbc:
            np.testing.assert_almost_equal(cp2k_and_ref[0].data['cells'],
                                        cp2k_and_ref[1].data['cells'],
                                        decimal = 4,
                                        err_msg = 'cell failed')

    def test_coord(self, cp2k_and_ref):
        assert cp2k_and_ref[0].get_nframes() == cp2k_and_ref[1].get_nframes()
        # think about direct coord
        tmp_cell = cp2k_and_ref[0].data['cells']
        tmp_cell = np.reshape(tmp_cell, [-1, 3])
        tmp_cell_norm = np.reshape(np.linalg.norm(tmp_cell, axis = 1), [-1, 1, 3])
        np.testing.assert_almost_equal(cp2k_and_ref[0].data['coords'] / tmp_cell_norm,
                                       cp2k_and_ref[1].data['coords'] / tmp_cell_norm,
                                       decimal = 6,
                                       err_msg = 'coord failed')

    def test_energy(self, cp2k_and_ref):
        np.testing.assert_almost_equal(
            cp2k_and_ref[0]['energies'],
            cp2k_and_ref[1]['energies'],
            decimal = 6,
            err_msg = 'energies failed'
            )
    def test_force(self, cp2k_and_ref):
        np.testing.assert_almost_equal(
            cp2k_and_ref[0]['forces'],
            cp2k_and_ref[1]['forces'],
            decimal = 6,
            err_msg = 'forces failed'
            )

    def test_virial(self, cp2k_and_ref):
        print(cp2k_and_ref[0])
        print(cp2k_and_ref[0].has_virial())
        if not cp2k_and_ref[0].has_virial():
            
            assert False == (cp2k_and_ref[1].has_virial())
            return
        print("if code works ok")
        np.testing.assert_almost_equal(
            cp2k_and_ref[0]['virials'],
            cp2k_and_ref[1]['virials'],
            decimal = 6,
            err_msg = 'virials failed'
            )



