from .utils import file_content, interpolate_spline
from .utils import au2A, au2eV
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import fft
from ase import Atom, Atoms


def square_wave_filter(x, l, cell_z):
    half_l = l/2
    x_1st, x_2nd = np.array_split(x, 2)
    y_1st = np.heaviside(half_l - np.abs(x_1st),0)/l
    y_2nd = np.heaviside(half_l - np.abs(x_2nd-cell_z),0)/l
    y = np.concatenate([y_1st, y_2nd])
    return y

# parse cp2kcube
class Cp2kCube:
    """
    timestep: unit ps
    """
    def __init__(self, cube_file_name, timestep=0):
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


    def get_stc(self):
        atom_list = []
        for i in range(self.num_atoms):
            stc_vals = file_content(self.file, (6+i, 6+i+1))
            stc_vals = stc_vals.split()
            atom = Atom(
                symbol=int(stc_vals[0]), 
                position=(float(stc_vals[2])*au2A, float(stc_vals[3])*au2A, float(stc_vals[4])*au2A)
                )
            atom_list.append(atom)

        stc = Atoms(atom_list)
        stc.set_cell([self.cell_x, self.cell_y, self.cell_z])
        return stc
        
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
            # set the last point same as first point
            points = np.append(points, length)
            vals = np.append(vals, vals[0])
            new_points = np.linspace(0, length, 4097)[:-1]
            new_points, new_vals = interpolate_spline(points, vals, new_points)
            return new_points, new_vals
        else:
            return points, vals
    
    def get_mav(self, l1, l2=0, ncov=1, interpolate=False):
        axis="z"
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
        plt.figure(figsize=(9,9), dpi=100)
        plt.plot(x, y, label=("PAV"+axis))
        plt.xlabel(axis + " [A]")
        plt.ylabel("Hartree [eV]")
        plt.legend()
        plt.savefig(os.path.join(output_dir, "pav.png"), dpi=100)



class Cp2kCubeTraj:
    def __init__(cube_dir, prefix):
        pass

