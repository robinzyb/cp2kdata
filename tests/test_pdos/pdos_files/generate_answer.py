from cp2kdata import Cp2kPdos
from pathlib import Path
import numpy as np
import json

files_list = [
    "bivo4-water-k1-1_0.pdos"
]

output_path = Path("case_1_pdos")

answer={}

for file in files_list:
    pdos = Cp2kPdos(output_path/file)
    answer["project_name"] = pdos.project_name
    answer["spin"] = pdos.spin
    answer["listidx"] = pdos.listidx
    answer["kind"] = pdos.kind
    answer["timestep"] = pdos.timestep
    answer["fermi"] = pdos.fermi
    answer["homo_ener"] = pdos.get_homo_ener()
    answer["lumo_ener"] = pdos.get_lumo_ener()

    np.save(output_path/"answer"/"dos.npy", pdos.get_dos())
    np.save(output_path/"answer"/"occupation.npy", pdos.occupation)

with open(output_path/"answer"/"answer.json", "w") as fp:
    json.dump(answer, fp, indent=4)