import os

import pytest
import numpy as np

from cp2kdata import Cp2kCube


path_prefix = "tests/test_cube/"
cube_list = [Cp2kCube(os.path.join(path_prefix, "Si_bulk8-v_hartree-1_0.cube"))]
answer_dir_list = [os.path.join(path_prefix, "answer_Si_bulk8-v_hartree-1_0.cube")]

test_params = list(zip(cube_list, answer_dir_list))


@pytest.fixture(params=test_params, scope='class')
def cube_and_answer(request):
    return request.param

class TestCp2kCube():
    def test_num_atoms(self, cube_and_answer):
        cube = cube_and_answer[0]
        answer_dir = cube_and_answer[1]
        num_atoms = cube.num_atoms
        num_atoms_answer = np.load(os.path.join(answer_dir, "num_atoms.npy"))
        assert num_atoms == num_atoms_answer
    def test_grid_point(self, cube_and_answer):
        cube = cube_and_answer[0]
        answer_dir = cube_and_answer[1]
        grid_point = cube.cell.grid_point
        grid_point_answer = np.load(os.path.join(answer_dir, "grid_point.npy"))
        assert np.all(grid_point == grid_point_answer)
    def test_grid_spacing_matrix(self, cube_and_answer):
        cube = cube_and_answer[0]
        answer_dir = cube_and_answer[1]
        gs_matrix = cube.cell.grid_spacing_matrix
        gs_matrix_answer = np.load(os.path.join(answer_dir, "gs_matrix.npy"))
        assert np.all(gs_matrix == gs_matrix_answer)
    def test_cube_vals(self, cube_and_answer):
        cube = cube_and_answer[0]
        answer_dir = cube_and_answer[1]
        cube_vals = cube.cube_vals
        cube_vals_answer = np.load(os.path.join(answer_dir, "cube_vals.npy"))
        assert np.all(cube_vals == cube_vals_answer)
    def test_pav(self, cube_and_answer):
        cube = cube_and_answer[0]
        answer_dir = cube_and_answer[1]
        pav_x, pav = cube.get_pav()
        pav_answer = np.load(os.path.join(answer_dir, "pav.npy"))
        pav_x_answer = pav_answer[0]
        pav_answer = pav_answer[1]
        assert np.all(pav == pav_answer)
        assert np.all(pav_x == pav_x_answer)
    def test_mav(self, cube_and_answer):
        cube = cube_and_answer[0]
        answer_dir = cube_and_answer[1]
        mav_x, mav = cube.get_mav(l1=1, l2=1, ncov=2)
        mav_answer = np.load(os.path.join(answer_dir, "mav.npy"))
        mav_x_answer = mav_answer[0]
        mav_answer = mav_answer[1]

        np.testing.assert_almost_equal(mav, 
                                       mav_answer, 
                                       decimal=8,
                                       err_msg = 'mav failed'
                                       )
        np.testing.assert_almost_equal(mav_x,
                                        mav_x_answer,
                                        decimal=8,
                                        err_msg = 'mav_x failed'
                                        )
        #assert np.all(mav == mav_answer)
        #assert np.all(mav_x == mav_x_answer)




