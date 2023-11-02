import pytest
import numpy as np
from ase.geometry.cell import cellpar_to_cell
from ase.geometry.cell import cell_to_cellpar
from cp2kdata.cell import Cp2kCell  # Replace 'your_module' with the actual module containing the Cp2kCell class.

class TestCp2kCell:
    # Define expected cell matrices for different cases
    def _create_expected_cell_matrix(self, cell_param):
        if isinstance(cell_param, float):
            return np.array([[cell_param, 0, 0], [0, cell_param, 0], [0, 0, cell_param]])
        elif cell_param.shape == (3,):
            return np.array([[cell_param[0], 0, 0], [0, cell_param[1], 0], [0, 0, cell_param[2]]])
        elif cell_param.shape == (6,):
            return cellpar_to_cell(cell_param)
        elif cell_param.shape == (3, 3):
            return cell_param
    def _create_expected_grid_spacing_matrix(self, cell_matrix, grid_point, grid_spacing_matrix):
        if (grid_point is None) and (grid_spacing_matrix is None):
            grid_point = None
            grid_spacing_matrix = None
            print("No grid point information")
        elif (grid_point is None) and (grid_spacing_matrix is not None):
            grid_spacing_matrix = grid_spacing_matrix
            grid_point = np.round(cell_matrix/grid_spacing_matrix)
        elif (grid_point is not None) and (grid_spacing_matrix is None):
            grid_point = np.array(grid_point)
            grid_spacing_matrix = cell_matrix/grid_point[:, np.newaxis]
        elif (grid_point is not None) and (grid_spacing_matrix is not None):
            grid_point = np.array(grid_point)
            grid_spacing_matrix = np.array(grid_spacing_matrix)
        return grid_spacing_matrix

    def _create_expected_cell_param(self, cell_param):
        if isinstance(cell_param, float):
            return np.array([cell_param, cell_param, cell_param, 90.0, 90.0, 90.0])
        elif cell_param.shape == (3,):
            return np.array([cell_param[0], cell_param[1], cell_param[2], 90.0, 90.0, 90.0])
        elif cell_param.shape == (6,):
            return cell_param
        elif cell_param.shape == (3, 3):
            return cell_to_cellpar(cell_param)

    # Define sample data using a fixture
    @pytest.fixture(params=[
        (np.array([10.0, 12.0, 15.0]), None, None),
        #(np.array([10.0, 12.0, 15.0]), None, np.array([[1.0, 0.0, 0.0],[0,1.0,0],[0,0,1.0]])),
        (np.array([10.0, 12.0, 15.0, 90.0, 90.0, 90.0]), None, None),
        (np.array([[10.0, 0, 0], [0, 12.0, 0], [0, 0, 15.0]]), [2, 2, 2], None)
    ])
    def sample_data(self, request):
        return request.param

    def test_constructor(self, sample_data):
        cell_param, grid_point, grid_spacing_matrix = sample_data
        cell = Cp2kCell(cell_param, grid_point, grid_spacing_matrix)
        assert np.array_equal(cell.cell_matrix, self._create_expected_cell_matrix(cell_param))

    def test_copy(self, sample_data):
        cell_param, grid_point, grid_spacing_matrix = sample_data
        cell = Cp2kCell(cell_param, grid_point, grid_spacing_matrix)
        copied_cell = cell.copy()
        assert np.array_equal(cell.cell_matrix, copied_cell.cell_matrix)
        assert np.array_equal(cell.grid_point, copied_cell.grid_point)
        assert np.array_equal(cell.grid_spacing_matrix, copied_cell.grid_spacing_matrix)

    def test_get_volume(self, sample_data):
        cell_param, grid_point, grid_spacing_matrix = sample_data
        cell = Cp2kCell(cell_param, grid_point, grid_spacing_matrix)
        expected_volume = np.linalg.det(self._create_expected_cell_matrix(cell_param))
        assert cell.get_volume() == expected_volume

    def test_get_dv(self, sample_data, capsys):
        cell_param, grid_point, grid_spacing_matrix = sample_data
        cell = Cp2kCell(cell_param, grid_point, grid_spacing_matrix)
        if (grid_point is None) and (grid_spacing_matrix is None):
            cell.get_dv() 
            captured = capsys.readouterr()
            assert captured.out.splitlines()[-1] == "No grid point information is available"
        else:
            print(cell.cell_matrix, grid_point, grid_spacing_matrix)
            expected_grid_spacing_matrix = self._create_expected_grid_spacing_matrix(cell.cell_matrix, grid_point, grid_spacing_matrix)
            expected_dv = np.linalg.det(expected_grid_spacing_matrix)
            assert cell.get_dv() == expected_dv

    def test_get_cell_param(self, sample_data):
        cell_param, grid_point, grid_spacing_matrix = sample_data
        cell = Cp2kCell(cell_param, grid_point, grid_spacing_matrix)
        expected_cell_param = self._create_expected_cell_param(cell_param)
        assert np.array_equal(cell.get_cell_param(), expected_cell_param)

    def test_get_cell_angles(self, sample_data):
        cell_param, grid_point, grid_spacing_matrix = sample_data
        cell = Cp2kCell(cell_param, grid_point, grid_spacing_matrix)
        expected_cell_param = self._create_expected_cell_param(cell_param)
        expected_cell_angles = expected_cell_param[3:]
        assert np.array_equal(cell.get_cell_angles(), expected_cell_angles)

    def test_get_cell_lengths(self, sample_data):
        cell_param, grid_point, grid_spacing_matrix = sample_data
        cell = Cp2kCell(cell_param, grid_point, grid_spacing_matrix)
        expected_cell_param = self._create_expected_cell_param(cell_param)
        expected_cell_lengths = expected_cell_param[:3]
        assert np.array_equal(cell.get_cell_lengths(), expected_cell_lengths)
