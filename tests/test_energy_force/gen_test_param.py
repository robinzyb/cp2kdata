# this is used to generate assert param for output, please check manually to ensure the corectness!
from cp2kdata.output import Cp2kOutput
import json
import numpy as np
import os

output_path = "v9.0/normal"

def print_array(array):
    for i in array:
        for j in i:
            print(j)

answer = {}
tmp = Cp2kOutput(os.path.join(output_path, "output"))
os.mkdir(os.path.join(output_path, "answer"))


answer["run_type"] = tmp.get_run_type()
answer["version"] = tmp.get_version_string()
answer["pot_energy"] = list(tmp.get_energies_list())
answer["chemical_symbols"] = list(tmp.get_chemical_symbols())
answer["chemical_symbols_fake"] = list(tmp.get_chemical_symbols_fake())
answer["atomic_kind"] = list(tmp.get_atomic_kind())
answer["atom_num"] = list(map(int, tmp.get_atom_num()))
answer["atom_kinds_list"] = list(map(int, tmp.get_atom_kinds_list()))

np.save(os.path.join(output_path, "answer", "init_cell.npy"), tmp.get_init_cell())
np.save(os.path.join(output_path, "answer", "atomic_init_coord.npy"), tmp.get_init_atomic_coordinates())
np.save(os.path.join(output_path, "answer", "atomic_forces_list.npy"), tmp.get_atomic_forces_list())
np.save(os.path.join(output_path, "answer", "stress_tensor_list.npy"), tmp.get_stress_tensor_list())

#np.save("mulliken_pop_list.npy", tmp.get_mulliken_pop_list())

print("="*20+" INIT COORD "+"="*20)
print_array(tmp.get_init_atomic_coordinates())
print("="*20+" FORCES "+"="*20)
print_array(tmp.get_atomic_forces_list())
print(tmp.get_init_cell())
print(tmp.get_stress_tensor_list())

with open(os.path.join(output_path, "answer", "answer.json"), "w") as fp:
    json.dump(answer, fp, indent=4)
