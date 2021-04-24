from .utils import file_content, interpolate_spline
from .utils import au2A, au2eV
import numpy as np
import matplotlib.pyplot as plt
import os


# parse cp2kcube
class Cp2kCube:
    """
    timestep: unit ps
    """
    def __init__(self, cube_file_name, timestep=0):
        self.file = cube_file_name
        self.timestep = timestep
        self.cube_vals = self.read_cube_vals()

    @property
    def num_atoms(self):
        line = file_content(self.file, 2)
        num_atoms = int(line.split()[0])
        return num_atoms

    @property
    def grid_size(self):
        # read grid point and grid size, unit: angstrom
        content_list = file_content(self.file, (3,6))
        content_list = content_list.split()
        num_x = int(content_list[0])
        num_y = int(content_list[4])
        num_z = int(content_list[8])
        return num_x, num_y, num_z

    @property
    def grid_space(self):
        # read grid point and grid size, unit: angstrom
        content_list = file_content(self.file, (3,6))
        content_list = content_list.split()
        step_x = float(content_list[1])*au2A
        step_y = float(content_list[6])*au2A
        step_z = float(content_list[11])*au2A
        return step_x, step_y, step_z

    def read_cube_vals(self):
        # read the cube value from file
        cube_vals = file_content(self.file, (6+self.num_atoms,))
        cube_vals = cube_vals.split()
        cube_vals = np.array(cube_vals, dtype = float)
        cube_vals = cube_vals.reshape(self.grid_size)
        cube_vals = cube_vals*au2eV
        return cube_vals

    def get_pav(self, axis="z", interpolate=False):
        # do the planar average along specific axis
        if axis == 'x':
            vals = self.cube_vals.mean(axis=(1,2))
            points = np.arange(0, self.grid_size[0])*self.grid_space[0]
            length = self.grid_size[0]*self.grid_space[0]
        elif axis == 'y':
            vals = self.cube_vals.mean(axis=(0,2))
            points = np.arange(0, self.grid_size[1])*self.grid_space[1]
            length = self.grid_size[1]*self.grid_space[1]
        elif axis == 'z':
            vals = self.cube_vals.mean(axis=(0,1))
            points = np.arange(0, self.grid_size[2])*self.grid_space[2]
            length = self.grid_size[2]*self.grid_space[2]
        else:
            print("not such plane average style!")

        # interpolate or note
        if interpolate:
            new_points = np.linspace(0, length, len(points)*10)
            new_points, new_vals = interpolate_spline(points, vals, new_points)
            return new_points, new_vals
        else:
            return points, vals

    def quick_plot(self, axis="z", interpolate=False, output_dir="./"):
        x, y = self.get_pav(axis=axis, interpolate=interpolate)
        plt.figure(figsize=(9,9), dpi=100)
        plt.plot(x, y, label=("PAV"+axis))
        plt.xlabel(axis + " [A]")
        plt.ylabel("Hartree [eV]")
        plt.legend()
        plt.savefig(os.path.join(output_dir, "pav.png"), dpi=100)



class Cp2kCubeTraj:
    def __init__(cube_dir, prefix):
        pass

