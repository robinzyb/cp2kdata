# this is used to generate assert param for output, please check manually to ensure the corectness!
from cp2kdata.output import Cp2kOutput
import json
import numpy as np

def print_array(array):
    for i in array:
        for j in i:
            print(j)

answer = {}
tmp = Cp2kOutput('./output')

answer["run_type"] = tmp.get_run_type()
answer["version"] = tmp.get_version_string()
answer["pot_energy"] = list(tmp.get_energies_list())
np.save("atomic_init_coord.npy", tmp.get_init_atomic_coordinates())
np.save("atomic_forces_list.npy", tmp.get_atomic_forces_list())
#np.save("mulliken_pop_list.npy", tmp.get_mulliken_pop_list())

print("="*20+" INIT COORD "+"="*20)
print_array(tmp.get_init_atomic_coordinates())
print("="*20+" FORCES "+"="*20)
print_array(tmp.get_atomic_forces_list())


with open("answer.json", "w") as fp:
    json.dump(answer, fp, indent=4)
