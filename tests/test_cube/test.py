from cp2kdata.cube import Cp2kCube
from ase.visualize import view

x = Cp2kCube("input.cube")
y=x.get_stc()
view(y)
