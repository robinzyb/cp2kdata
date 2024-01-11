from cp2kdata.utils import file_content, interpolate_spline
from cp2kdata.utils import au2A, au2eV
from cp2kdata.cell import Cp2kCell
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import fft
from ase import Atom, Atoms
from monty.json import MSONable
from copy import deepcopy
import asciichartpy as acp


def square_wave_filter(x, l, cell_z):
    half_l = l/2
    x_1st, x_2nd = np.array_split(x, 2)
    y_1st = np.heaviside(half_l - np.abs(x_1st), 0)/l
    y_2nd = np.heaviside(half_l - np.abs(x_2nd-cell_z), 0)/l
    y = np.concatenate([y_1st, y_2nd])
    return y

# parse cp2kcube


class Cp2kCubeOld:
    """
    timestep: unit ps
    """

    def __init__(self, cube_file_name, timestep=0):
        print("Warning: This is Cp2kCubeOld is deprecated after version 0.6.x, use Cp2kCube instead!")
        print("Warning: to use old one, from cp2kdata.cube.cube import Cp2kCubeOld")
        self.file = cube_file_name
        self.timestep = timestep
        self.cube_vals = self.read_cube_vals()
        self.cell_x = self.grid_size[0]*self.grid_space[0]
        self.cell_y = self.grid_size[1]*self.grid_space[1]
        self.cell_z = self.grid_size[2]*self.grid_space[2]

    @property
    def num_atoms(self):
        line = file_content(self.file, 2)
        num_atoms = int(line.split()[0])
        return num_atoms

    @property
    def grid_size(self):
        # read grid point and grid size, unit: angstrom
        content_list = file_content(self.file, (3, 6))
        content_list = content_list.split()
        num_x = int(content_list[0])
        num_y = int(content_list[4])
        num_z = int(content_list[8])
        return num_x, num_y, num_z

    @property
    def grid_space(self):
        # read grid point and grid size, unit: angstrom
        content_list = file_content(self.file, (3, 6))
        content_list = content_list.split()
        step_x = float(content_list[1])*au2A
        step_y = float(content_list[6])*au2A
        step_z = float(content_list[11])*au2A
        return step_x, step_y, step_z

    def get_stc(self):
        atom_list = []
        for i in range(self.num_atoms):
            stc_vals = file_content(self.file, (6+i, 6+i+1))
            stc_vals = stc_vals.split()
            atom = Atom(
                symbol=int(stc_vals[0]),
                position=(
                    float(stc_vals[2])*au2A, float(stc_vals[3])*au2A, float(stc_vals[4])*au2A)
            )
            atom_list.append(atom)

        stc = Atoms(atom_list)
        stc.set_cell([self.cell_x, self.cell_y, self.cell_z])
        return stc

    def read_cube_vals(self):
        # read the cube value from file
        cube_vals = file_content(self.file, (6+self.num_atoms,))
        cube_vals = cube_vals.split()
        cube_vals = np.array(cube_vals, dtype=float)
        cube_vals = cube_vals.reshape(self.grid_size)
        cube_vals = cube_vals*au2eV
        return cube_vals

    def get_pav(self, axis="z", interpolate=False):
        # do the planar average along specific axis
        if axis == 'x':
            vals = self.cube_vals.mean(axis=(1, 2))
            points = np.arange(0, self.grid_size[0])*self.grid_space[0]
            length = self.grid_size[0]*self.grid_space[0]
        elif axis == 'y':
            vals = self.cube_vals.mean(axis=(0, 2))
            points = np.arange(0, self.grid_size[1])*self.grid_space[1]
            length = self.grid_size[1]*self.grid_space[1]
        elif axis == 'z':
            vals = self.cube_vals.mean(axis=(0, 1))
            points = np.arange(0, self.grid_size[2])*self.grid_space[2]
            length = self.grid_size[2]*self.grid_space[2]
        else:
            print("not such plane average style!")

        # interpolate or note
        if interpolate:
            # set the last point same as first point
            points = np.append(points, length)
            vals = np.append(vals, vals[0])
            new_points = np.linspace(0, length, 4097)[:-1]
            new_points, new_vals = interpolate_spline(points, vals, new_points)
            return new_points, new_vals
        else:
            return points, vals

    def get_mav(self, l1, l2=0, ncov=1, interpolate=False):
        axis = "z"
        pav_x, pav = self.get_pav(axis=axis, interpolate=interpolate)
        theta_1_fft = fft.fft(square_wave_filter(pav_x, l1, self.cell_z))
        pav_fft = fft.fft(pav)
        mav_fft = pav_fft*theta_1_fft*self.cell_z/len(pav_x)
        if ncov == 2:
            theta_2_fft = fft.fft(square_wave_filter(pav_x, l2, self.cell_z))
            mav_fft = mav_fft*theta_2_fft*self.cell_z/len(pav_x)
        mav = fft.ifft(mav_fft)
        return pav_x, np.real(mav)

    def quick_plot(self, axis="z", interpolate=False, output_dir="./"):
        x, y = self.get_pav(axis=axis, interpolate=interpolate)
        plt.figure(figsize=(9, 9), dpi=100)
        plt.plot(x, y, label=("PAV"+axis))
        plt.xlabel(axis + " [A]")
        plt.ylabel("Hartree [eV]")
        plt.legend()
        plt.savefig(os.path.join(output_dir, "pav.png"), dpi=100)


class Cp2kCube(MSONable):
    # add MSONable use as_dict and from_dict
    """
    Documentation for the Cp2kCube class.
    """

    def __init__(self, fname=None, cube_vals=None, cell=None, stc=None):
        print("Warning: This is New Cp2kCube Class, if you want to use old Cp2kCube")
        print("try, from cp2kdata.cube.cube import Cp2kCubeOld")
        print("New Cp2kCube return raw values in cp2k cube file")
        print("that is, length in bohr and energy in hartree for potential file")
        print("that is, length in bohr and density in e/bohr^3 for density file")
        print("to convert unit: try from cp2kdata.utils import au2A, au2eV")

        self.file = fname

        if cell is None:
            self.cell = self.read_cell()
        else:
            self.cell = cell
        if stc is None:
            self.stc = self.get_stc()
        else:
            self.stc = stc

        if cube_vals is None:
            self.cube_vals = self.read_cube_vals(self.file,
                                                 self.num_atoms,
                                                 self.cell.grid_point
                                                 )
        else:
            self.cube_vals = cube_vals

    def read_cell(self):
        grid_point = self.read_grid_point(self.file)
        gs_matrix = self.read_gs_matrix(self.file)
        cell_param = gs_matrix*grid_point[:, np.newaxis]
        return Cp2kCell(cell_param, grid_point, gs_matrix)

    @property
    def num_atoms(self):
        line = file_content(self.file, 2)
        num_atoms = int(line.split()[0])
        return num_atoms

    def as_dict(self):
        """Returns data dict of Cp2kCube instance."""
        data_dict = {
            "@module": self.__class__.__module__,
            "@class": self.__class__.__name__,
            "file": self.file,
            "cube_vals": self.cube_vals,
            "cell": self.cell,
            "stc": self.stc,
        }
        return data_dict

    def __add__(self, others):
        """magic method for adding two Cp2kCube instances"""
        self_copy = self.copy()
        if isinstance(others, Cp2kCube):
            other_copy = others.copy()
            other_copy.cube_vals = self_copy.cube_vals + other_copy.cube_vals
        else:
            raise RuntimeError("Unspported Class")
        return other_copy

    def __sub__(self, others):
        """magic method for subtracting two Cp2kCube instances"""
        self_copy = self.copy()
        if isinstance(others, Cp2kCube):
            other_copy = others.copy()
            other_copy.cube_vals = self_copy.cube_vals - other_copy.cube_vals
        else:
            raise RuntimeError("Unspported Class")
        return other_copy

    def get_stc(self):
        atom_list = []
        for i in range(self.num_atoms):
            stc_vals = file_content(self.file, (6+i, 6+i+1))
            stc_vals = stc_vals.split()
            atom = Atom(
                symbol=int(stc_vals[0]),
                position=(
                    float(stc_vals[2])*au2A, float(stc_vals[3])*au2A, float(stc_vals[4])*au2A)
            )
            atom_list.append(atom)

        stc = Atoms(atom_list)
        stc.set_cell(self.cell.cell_matrix*au2A)
        return stc

    def copy(self):
        return deepcopy(self)

    def get_pav(self, axis='z', interpolate=False):


        # do the planar average along specific axis
        lengths = self.cell.get_cell_lengths()
        grid_point = self.cell.grid_point
        gs_matrix = self.cell.grid_spacing_matrix
        if axis == 'x':
            vals = self.cube_vals.mean(axis=(1, 2))
            points = np.arange(0, grid_point[0])*gs_matrix[0][0]
            length = lengths[0]

            np.testing.assert_array_equal(
                self.cell.get_cell_angles()[[1,2]],
                np.array([90.0, 90.0]),
                err_msg=f"The axis x is not perpendicular to yz plane, the pav can not be used!"
            )

        elif axis == 'y':
            vals = self.cube_vals.mean(axis=(0, 2))
            points = np.arange(0, grid_point[1])*gs_matrix[1][1]
            length = lengths[1]

            np.testing.assert_array_equal(
                self.cell.get_cell_angles()[[0, 2]],
                np.array([90.0, 90.0]),
                err_msg=f"The axis y is not perpendicular to xz plane, the pav can not be used!"
            )

        elif axis == 'z':
            vals = self.cube_vals.mean(axis=(0, 1))
            points = np.arange(0, grid_point[2])*gs_matrix[2][2]
            length = lengths[2]

            np.testing.assert_array_equal(
                self.cell.get_cell_angles()[[0,1]],
                np.array([90.0, 90.0]),
                err_msg=f"The axis z is not perpendicular to xy plane, the pav can not be used!"
            )

        else:
            print("not such plane average style, the avaialble options are 'x', 'y', 'z'")

        # interpolate or note
        if interpolate:
            # set the last point same as first point
            points = np.append(points, length)
            vals = np.append(vals, vals[0])
            new_points = np.linspace(0, length, 4097)[:-1]
            new_points, new_vals = interpolate_spline(points, vals, new_points)
            return new_points, new_vals
        else:
            return points, vals

    def get_mav(self, l1, l2=0, ncov=1, interpolate=False, axis="z"):
        cell_length = {
            "x": self.cell.get_cell_lengths()[0],
            "y": self.cell.get_cell_lengths()[1],
            "z": self.cell.get_cell_lengths()[2]
        }
        length = cell_length[axis]

        pav_x, pav = self.get_pav(axis=axis, interpolate=interpolate)
        theta_1_fft = fft.fft(square_wave_filter(pav_x, l1, length))
        pav_fft = fft.fft(pav)
        mav_fft = pav_fft*theta_1_fft*length/len(pav_x)
        if ncov == 2:
            theta_2_fft = fft.fft(square_wave_filter(pav_x, l2, length))
            mav_fft = mav_fft*theta_2_fft*length/len(pav_x)
        mav = fft.ifft(mav_fft)
        return pav_x, np.real(mav)

    def quick_plot(self, axis="z", interpolate=False):

        x, y = self.get_pav(axis=axis, interpolate=interpolate)
        plt.style.use('cp2kdata.matplotlibstyle.jcp')
        row = 1
        col = 1
        fig = plt.figure(figsize=(3.37*col, 1.89*row),
                         dpi=600, facecolor='white')
        gs = fig.add_gridspec(row, col)
        ax = fig.add_subplot(gs[0])
        ax.plot(x, y, label=(f"PAV along {axis}"))
        # ax.set_xlabel(f'{axis} [A]')
        # ax.set_ylabel('Hartree [eV]')
        ax.legend()
        return fig

    def view_cube_acsii(self, axis='z', mav=False, l1=None, l2=None, ncov=1, unit='au', width=135):
        if mav:
            x, y = self.get_mav(l1, l2, ncov, axis=axis)
        else:
            x, y = self.get_pav(axis=axis)

        if unit == 'au':
            pass
        elif unit == 'eV':
            y = y*au2eV
        else:
            print("not such unit, the available options are 'au' and 'eV'")
        step = int(len(y)/width)
        print(acp.plot(y[::step], {'height': 20}))

    def write_cube(self, fname, comments='#'):
        grid_point = self.cell.grid_point
        gs_matrix = self.cell.grid_spacing_matrix
        with open(fname, 'w') as fw:
            # write header
            fw.write('Cube file generated by CP2KData\n')
            fw.write(comments+'\n')
            # grid information
            fw.write(f'{self.num_atoms:5d}{0:12.6f}{0:12.6f}{0:12.6f}\n')
            fw.write(
                f'{grid_point[0]:5d}{gs_matrix[0][0]:12.6f}{gs_matrix[0][1]:12.6f}{gs_matrix[0][2]:12.6f}\n')
            fw.write(
                f'{grid_point[1]:5d}{gs_matrix[1][0]:12.6f}{gs_matrix[1][1]:12.6f}{gs_matrix[1][2]:12.6f}\n')
            fw.write(
                f'{grid_point[2]:5d}{gs_matrix[2][0]:12.6f}{gs_matrix[2][1]:12.6f}{gs_matrix[2][2]:12.6f}\n')
            # structure information
            for atom in self.stc:
                fw.write(
                    f'{atom.number:5d}{0:12.6f}{atom.position[0]/au2A:12.6f}{atom.position[1]/au2A:12.6f}{atom.position[2]/au2A:12.6f}\n')
            # cube values
            # cp2k write cube loop in z, y, x order
            # https://github.com/cp2k/cp2k/blob/01090ebf0718ff6885d11f89fe10938d80eb0a02/src/pw/realspace_grid_cube.F#L99
            for i in range(grid_point[0]):
                for j in range(grid_point[1]):
                    for k in range(grid_point[2]):
                        # notice that cp2k write scientific notion differntly
                        # cp2k:   0.20871E+00
                        # python: 2.08710E-01
                        fw.write(f'{self.cube_vals[i,j,k]:13.5E}')
                        if (k+1) % 6 == 0:
                            fw.write('\n')
                    # write a blank line after each z value
                    if grid_point[2] % 6 != 0:
                        fw.write('\n')

    def get_integration(self):
        dv = self.cell.get_dv()
        result = np.sum(self.cube_vals)*dv
        return result

    def get_cell(self):
        return self.cell.copy()

    def reduce_resolution(self, stride, axis='xyz'):
        new_cube = self.copy()

        stride_dict = {
            "xyz": np.array([stride, stride, stride]),
            "xy": np.array([stride, stride, 1]),
            "xz": np.array([stride, 1, stride]),
            "yz": np.array([1, stride, stride]),
            "x": np.array([stride, 1, 1]),
            "y": np.array([1, stride, 1]),
            "z": np.array([1, 1, stride])
        }
        stride_array = stride_dict[axis]
        # reduce the grid point
        grid_point = self.cell.grid_point
        grid_point = np.floor((grid_point-1)/stride_array) + 1
        grid_point = grid_point.astype(int)
        new_cube.cell.grid_point = grid_point

        # increase the grid spacing
        new_cube.cell.grid_spacing_matrix = self.cell.grid_spacing_matrix * \
            stride_array[:, np.newaxis]

        new_cube.cube_vals = self.cube_vals[::stride_array[0],
                                            ::stride_array[1], ::stride_array[2]]

        return new_cube

    @staticmethod
    def read_gs_matrix(fname):
        content_list = file_content(fname, (3, 6))
        content_list = content_list.split()

        gs_matrix = [
            [float(content_list[1]), float(
                content_list[2]), float(content_list[3])],
            [float(content_list[5]), float(
                content_list[6]), float(content_list[7])],
            [float(content_list[9]), float(
                content_list[10]), float(content_list[11])]
        ]
        gs_matrix = np.array(gs_matrix)
        return gs_matrix

    @staticmethod
    def read_grid_point(fname):
        # read grid point and grid size, unit: angstrom
        content_list = file_content(fname, (3, 6))
        content_list = content_list.split()
        num_x = int(content_list[0])
        num_y = int(content_list[4])
        num_z = int(content_list[8])
        return np.array([num_x, num_y, num_z])

    @staticmethod
    def read_cube_vals(fname, num_atoms, grid_point):
        # read the cube value from file
        cube_vals = file_content(fname, (6+num_atoms,))
        cube_vals = cube_vals.split()
        cube_vals = np.array(cube_vals, dtype=float)
        cube_vals = cube_vals.reshape(grid_point)
        return cube_vals


class Cp2kCubeTraj:
    def __init__(cube_dir, prefix):
        pass
