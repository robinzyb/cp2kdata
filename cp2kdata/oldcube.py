from toolkit.utils import file_content
from toolkit.utils import au2A, au2eV
import numpy as np


def read_cube_num_atom(cube_file):
    # read the number of atoms in cube file, cp2k format
    line = file_content(cube_file, 2)
    num_atom = int(line.split()[0])
    return num_atom

def read_cube_grid(cube_file):
    # read grid point and grid size, unit: angstrom
    content_list = file_content(cube_file, (3,6))
    content_list = content_list.split()
    num_x = int(content_list[0])
    num_y = int(content_list[4])
    num_z = int(content_list[8])
    step_x = float(content_list[1])*au2A
    step_y = float(content_list[6])*au2A
    step_z = float(content_list[11])*au2A
    return (num_x, num_y, num_z), (step_x, step_y, step_z)

def read_cube_pos(cube_file, num_atom):
    # read the position information from cube
    pos = file_content(cube_file, (6,6+num_atom)).split()
    pos = np.array(pos, dtype = float)
    pos = pos.reshape(num_atom, int(len(pos)/num_atom))
    elements = pos[:, 0]
    pos = pos[:, 2:] * au2A
    return elements, pos

def read_cube_val(cube_file, num_atom, num_point):
    # read the cube value from file
    cube_val = file_content(cube_file, (6+num_atom,))
    cube_val = cube_val.split()
    cube_val = np.array(cube_val, dtype = float)
    cube_val = cube_val.reshape(num_point)
    return cube_val

def read_cube(cube_file):
    # collect the information from cp2k cube file
    info = {}
    info["num_atom"] = read_cube_num_atom(cube_file)
    info["num_point"], info["step"] = read_cube_grid(cube_file)
    info["elements"], info["pos"] = read_cube_pos(cube_file, info["num_atom"])
    info["cube_val"] = read_cube_val(cube_file, info["num_atom"], info["num_point"])
    return info

def cube_pav(cube_file, axis, interpolate=True):
    # do the planar average along specific axis
    cube_info = read_cube(cube_file)
    if axis == 'x':
        vals = cube_info["cube_val"].mean(axis=(1,2))*au2eV
        points = np.arange(0, cube_info["num_point"][0])*cube_info["step"][0]
        length = cube_info["num_point"][0]*cube_info["step"][0]
    elif axis == 'y':
        vals = cube_info["cube_val"].mean(axis=(0,2))*au2eV
        points = np.arange(0, cube_info["num_point"][1])*cube_info["step"][1]
        length = cube_info["num_point"][1]*cube_info["step"][1]
    elif axis == 'z':
        vals = cube_info["cube_val"].mean(axis=(0,1))*au2eV
        points = np.arange(0, cube_info["num_point"][2])*cube_info["step"][2]
        length = cube_info["num_point"][2]*cube_info["step"][2]
    else:
        print("not implement average style!")

    # interpolate or note
    if interpolate:
        new_points = np.linspace(0, length, len(points)*10)
        new_points, new_vals = interpolate_spline(points, vals, new_points)
        return new_points, new_vals
    else:
        return points, vals

def interpolate_spline(old_x, old_y, new_x):
    from scipy import interpolate
    f = interpolate.splrep(old_x, old_y, s=0)
    new_y = interpolate.splev(new_x, f)
    return new_x, new_y
