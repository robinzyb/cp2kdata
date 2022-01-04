# CP2KDATA

Python Package to postprocess cp2k data.

including cube file, pdos file, output file

- [CP2KDATA](#cp2kdata)
  - [Installation](#installation)
  - [Processing Output File](#processing-output-file)
    - [Processing ENERGY and FORCE Calculation](#processing-energy-and-force-calculation)
    - [Processing GEOMETRY OPTIMIZATION Calculation](#processing-geometry-optimization-calculation)
  - [Processing Cube File](#processing-cube-file)
  - [Processing PDOS File](#processing-pdos-file)
    - [Processing Single PDOS File](#processing-single-pdos-file)
    - [Quickplot of  PDOS Files in Single Point Energy Calculation](#quickplot-of--pdos-files-in-single-point-energy-calculation)

## Installation

```bash
pip install .
```



## Processing Output File

### Processing ENERGY and FORCE Calculation
```python
from cp2kdata.output import Cp2kOutput
cp2k_output_file = "output_energy_force"
cp2koutput=Cp2kOutput(cp2k_output_file)
# get the version of cp2k
print(cp2koutput.get_version_string())
# get the run type
print(cp2koutput.get_run_type())
# symbols with true element
print(cp2koutput.get_chemical_symbols())
# symbols with your set in input
print(cp2koutput.get_chemical_symbols_fake())

```

### Processing GEOMETRY OPTIMIZATION Calculation
```python
from cp2kdata.output import Cp2kOutput
cp2k_output_file = "output_geo_opt"
cp2koutput=Cp2kOutput(cp2k_output_file)
# get the version of cp2k
print(cp2koutput.get_version_string())
# get the run type
print(cp2koutput.get_run_type())
# get potential energy
print(cp2koutput.get_energies_list())
# get initial coordinates
print(cp2koutput.get_init_atomic_coordinates())
# symbols with true element
print(cp2koutput.get_chemical_symbols())
# symbols with your set in input
print(cp2koutput.get_chemical_symbols_fake())
# get the geometry optimization information
print(cp2koutput.get_geo_opt_info())
# quick plot of geometry optimization information 
cp2koutput.get_geo_opt_info_plot()
```
![geo_opt_plot](./figures/geo_opt_info.png)

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

### Processing Single PDOS File

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

