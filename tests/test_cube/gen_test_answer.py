import numpy as np
import os
from cp2kdata import Cp2kCube

file_list = ["Si_bulk8-v_hartree-1_0.cube"]


for file in file_list:
    cube = Cp2kCube(file)
    dir_name = f"answer_{file}"
    os.makedirs(dir_name, exist_ok = True)
    np.save(os.path.join(dir_name, "cube_vals.npy"), cube.cube_vals)
    np.save(os.path.join(dir_name, "grid_point.npy"), cube.cell.grid_point)
    np.save(os.path.join(dir_name, "gs_matrix.npy"), cube.cell.grid_spacing_matrix)
    np.save(os.path.join(dir_name, "num_atoms.npy"), cube.num_atoms)
    np.save(os.path.join(dir_name, "integration_all.npy"), cube.get_integration())
    np.save(os.path.join(dir_name, "integration_x_5.0_7.0.npy"), cube.get_integration(start_x=5.0, end_x=7.0))
    np.save(os.path.join(dir_name, "integration_y_5.0_7.0.npy"), cube.get_integration(start_y=5.0, end_y=7.0))
    np.save(os.path.join(dir_name, "integration_z_5.0_7.0.npy"), cube.get_integration(start_z=5.0, end_z=7.0))
    np.save(os.path.join(dir_name, "pav.npy"), cube.get_pav())
    np.save(os.path.join(dir_name, "mav.npy"), cube.get_mav(l1=1, l2=1, ncov=2))
    cube.write_cube(os.path.join(dir_name, "created_ref.cube"))
