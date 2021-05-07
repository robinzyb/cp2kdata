# CP2KDATA

Python Package to postprocess cp2k data.

including cube file, pdos file, output file

## Installation

```bash
pip install .
```



## Processing Cube File

```python
from cp2kdata.cube import Cp2kCube
cube_file = "xxx.cube"
mycube = Cp2kCube(cube_file)
# get Planar average data
mycube.get_pav(axis="z")
# quick plot
mycube.quick_plot(axis="z", interpolate=False, output_dir="./")
```



## Processing PDOS File

### Process Single PDOS File

```python
from cp2kdata.pdos import Pdos
dosfile = "Universality-ALPHA_k2-1_50.pdos"
mypdos = Pdos(dosfile)
dos, ener = mypdos.get_dos()
```

### Quickplot of  PDOS Files in Single Point Energy Calculation

```python
from cp2kdata.pdos import quick_plot_uks, quick_plot_rks
Calculation_dir = "./"
# if uks calculation use this
quick_plot_uks(Calculation_dir)
# if rks calculation use this 
quick_plot_rks(Calculation_dir)
```

