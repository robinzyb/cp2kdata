from ase.geometry.cell import cellpar_to_cell
from ase.geometry.cell import cell_to_cellpar
import numpy.typing as npt
import numpy as np
from numpy.linalg import LinAlgError
from copy import deepcopy


class Cp2kCell:
    def __init__(
        self,
        cell_param: npt.NDArray[np.float64],
        grid_point: npt.NDArray[np.int_] = None,
        grid_spacing_matrix: npt.NDArray[np.float64] = None
    ):
        """
        The documentation of Cell class used in cp2kdata
        Parameters
        ----------
        cell_param: np. array
            The length of the cell in bohr
        divi: np. array
            The number of grid points in each direction
        h: float
            The grid spacing in bohr

        a b c alpha beta gamma
        grid_point   : array
        grid_spacing_matrix : matrix 3x3
        """

        if isinstance(cell_param, float):
            self.cell_matrix = np.array(
                [
                    [cell_param, 0, 0],
                    [0, cell_param, 0],
                    [0, 0, cell_param]
                ]
            )
            print("input cell_param is a float, the cell is assumed to be cubic")
        elif cell_param.shape == (3,):
            self.cell_matrix = np.array(
                [
                    [cell_param[0], 0, 0],
                    [0, cell_param[1], 0],
                    [0, 0, cell_param[2]]
                ]
            )
            print("the length of input cell_param is 3, "
                  "the cell is assumed to be orthorhombic")
        elif cell_param.shape == (6,):
            self.cell_matrix = cellpar_to_cell(cell_param)
            print("the length of input cell_param is 6, "
                  "the Cp2kCell assumes it is [a, b, c, alpha, beta, gamma], "
                  "which will be converted to cell matrix")
        elif cell_param.shape == (3, 3):
            self.cell_matrix = cell_param
            print("input cell_param is a matrix with shape of (3,3), "
                  "the cell is read as is")
        else:
            raise ValueError("The input cell_param is not supported")

        if (grid_point is None) and (grid_spacing_matrix is None):
            self.grid_point = None
            self.grid_spacing_matrix = None
            print("No grid point information")
        elif (grid_point is None) and (grid_spacing_matrix is not None):
            self.grid_spacing_matrix = grid_spacing_matrix
            self.grid_point = np.round(
                self.cell_matrix/self.grid_spacing_matrix)
        elif (grid_point is not None) and (grid_spacing_matrix is None):
            self.grid_point = np.array(grid_point)
            self.grid_spacing_matrix = self.cell_matrix / \
                self.grid_point[:, np.newaxis]
        elif (grid_point is not None) and (grid_spacing_matrix is not None):
            self.grid_point = np.array(grid_point)
            self.grid_spacing_matrix = np.array(grid_spacing_matrix)

        if grid_point is not None:
            self.grid_point = self.grid_point.astype(int)

        self.cell_param = cell_to_cellpar(self.cell_matrix)

    def copy(self):
        return deepcopy(self)

    def get_volume(self):
        return np.linalg.det(self.cell_matrix)

    def get_dv(self):
        try:
            return np.linalg.det(self.grid_spacing_matrix)
        except LinAlgError as ae:
            print("No grid point information is available")

    def get_cell_param(self):
        return self.cell_param

    def get_cell_angles(self):
        return self.cell_param[3:]

    def get_cell_lengths(self):
        return self.cell_param[:3]
