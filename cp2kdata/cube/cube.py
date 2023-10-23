from cp2kdata.utils import file_content, interpolate_spline
from cp2kdata.utils import au2A, au2eV
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
    y_1st = np.heaviside(half_l - np.abs(x_1st),0)/l
    y_2nd = np.heaviside(half_l - np.abs(x_2nd-cell_z),0)/l
    y = np.concatenate([y_1st, y_2nd])
    return y

# parse cp2kcube
class Cp2kCubeOld:
    """
    timestep: unit ps
    """
    def __init__(self, cube_file_name, timestep=0):
        print("Warning: This Cp2kCube will be deprecated in version 0.6.x, use Cp2kCubeNew instead!")
        print("After version 0.6.x, Cp2kCube will be removed from cp2kdata.cube.cube")
        print("Cp2kCubeNew will be renamed as Cp2kCube")
        print("Test Cp2kCubeNew in your old code before upgrade to 0.6.x")
        print("Usage: from cp2kdata.cube.cube import Cp2kCubeNew as Cp2kCube")
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


class Cp2kCube(MSONable):
    # remove useless timestep argument
    # add MSONable use as_dict and from_dict
    # add copy method
    # add addition and subtraction method cube1 + cube2

    #TODO: .write method to write a cube file
    #TODO: complete parse the grid_spacing and num_grid


    
    def __init__(self, file=None, cube_vals=None, grid_size=None, grid_space=None, stc=None):
        print("Warning: This is New Cp2kCube Class, if you want to use old Cp2kCube")
        print("try, from cp2kdata.cube.cube import Cp2kCube")
        print("New Cp2kCube return raw values in cp2k cube file")
        print("that is, length in bohr and energy in hartree for potential file")
        print("that is, length in bohr and density in e/bohr^3 for density file")
        print("to convert unit: try from cp2kdata.utils import au2A, au2eV")

        self.file = file
        self.cube_vals = self.read_cube_vals()
        self.cell_x = self.grid_size[0]*self.grid_space[0]
        self.cell_y = self.grid_size[1]*self.grid_space[1]
        self.cell_z = self.grid_size[2]*self.grid_space[2]
        self.stc = self.get_stc()

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
        step_x = float(content_list[1])
        step_y = float(content_list[6])
        step_z = float(content_list[11])
        return step_x, step_y, step_z
    
    def as_dict(self):
        """Returns data dict of System instance."""
        data_dict = {
            "@module": self.__class__.__module__,
            "@class": self.__class__.__name__,
            "file": self.file,
            "cube_vals": self.cube_vals,
            "grid_size": self.grid_size,
            "grid_space": self.grid_space,
            "stc": self.stc,
            }
        return data_dict

    def __add__(self, others):
        """magic method for adding two Cp2kCube instances"""
        self_copy = self.copy()
        if isinstance(others, Cp2kCube):
            other_copy = others.copy()
            self_copy.cube_vals += other_copy.cube_vals
        else:
            raise RuntimeError("Unspported Class")
        return self_copy
    
    def __sub__(self, others):
        """magic method for subtracting two Cp2kCube instances"""
        self_copy = self.copy()
        if isinstance(others, Cp2kCube):
            other_copy = others.copy()
            self_copy.cube_vals -= other_copy.cube_vals
        else:
            raise RuntimeError("Unspported Class")
        return self_copy
        

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
    
    def copy(self):
        return deepcopy(self)
        
    def read_cube_vals(self):
        # read the cube value from file
        cube_vals = file_content(self.file, (6+self.num_atoms,))
        cube_vals = cube_vals.split()
        cube_vals = np.array(cube_vals, dtype = float)
        cube_vals = cube_vals.reshape(self.grid_size)
        return cube_vals

    def get_pav(self, axis='z', interpolate=False):
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
            "x": self.cell_x,
            "y": self.cell_y,
            "z": self.cell_z
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
        fig = plt.figure(figsize=(3.37*col, 1.89*row), dpi=600, facecolor='white')
        gs = fig.add_gridspec(row,col)
        ax  = fig.add_subplot(gs[0])
        ax.plot(x, y, label=(f"PAV along {axis}"))
        #ax.set_xlabel(f'{axis} [A]')
        #ax.set_ylabel('Hartree [eV]')
        ax.legend()
        return fig


    def view_cube_acsii(self, axis='z', mav=False, l1=None, l2=None, ncov=1, unit='au'):
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
        step = int(len(y)/135)
        print(acp.plot(y[::step], {'height': 20}))
    
    def write_cube(self, fname, comments='#'):
        with open(fname, 'w') as fw:
            # write header
            fw.write('Cube file generated by CP2KData\n')
            fw.write(comments+'\n')
            # grid information
            fw.write(f'{self.num_atoms:5d}{0:12.6f}{0:12.6f}{0:12.6f}\n')
            fw.write(f'{self.grid_size[0]:5d}{self.grid_space[0]:12.6f}{0.0:12.6f}{0:12.6f}\n')
            fw.write(f'{self.grid_size[1]:5d}{0.0:12.6f}{self.grid_space[1]:12.6f}{0:12.6f}\n')
            fw.write(f'{self.grid_size[2]:5d}{0.0:12.6f}{0.0:12.6f}{self.grid_space[2]:12.6f}\n')
            # structure information
            for atom in self.stc:
                fw.write(f'{atom.number:5d}{0:12.6f}{atom.position[0]/au2A:12.6f}{atom.position[1]/au2A:12.6f}{atom.position[2]/au2A:12.6f}\n')
            # cube values
            # cp2k write cube loop in z, y, x order
            # https://github.com/cp2k/cp2k/blob/01090ebf0718ff6885d11f89fe10938d80eb0a02/src/pw/realspace_grid_cube.F#L99
            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    for k in range(self.grid_size[2]):
                        # notice that cp2k write scientific notion differntly
                        # cp2k:   0.20871E+00
                        # python: 2.08710E-01
                        fw.write(f'{self.cube_vals[i,j,k]:13.5E}')
                        if (k+1)%6 == 0:
                            fw.write('\n')
                    # write a blank line after each z value 
                    if self.grid_size[2]%6 != 0:
                        fw.write('\n')
    

            
class Cp2kCubeTraj:
    def __init__(cube_dir, prefix):
        pass

