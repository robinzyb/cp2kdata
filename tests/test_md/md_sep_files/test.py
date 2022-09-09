import dpdata
import numpy as np


x=dpdata.LabeledSystem(file_name=".", cells=np.full((7, 3,3), 1), fmt="cp2kdata/md")
print(x)
print(x['cells'])