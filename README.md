# CP2KDATA


[![Python package](https://github.com/robinzyb/cp2kdata/actions/workflows/ci.yml/badge.svg)](https://github.com/robinzyb/cp2kdata/actions/workflows/ci.yml)[![Coverage Status](https://coveralls.io/repos/github/robinzyb/cp2kdata/badge.svg)](https://coveralls.io/github/robinzyb/cp2kdata)
![pythonv](https://img.shields.io/pypi/pyversions/cp2kdata)
![pypiv](https://img.shields.io/pypi/v/cp2kdata)

Python Package to postprocess cp2k data.

including cube file, pdos file, output file

- [CP2KDATA](#cp2kdata)
  - [Installation](#installation)
  - [Processing Output File](#processing-output-file)
    - [Basick Usage](#basick-usage)
    - [Processing ENERGY and FORCE Calculation](#processing-energy-and-force-calculation)
    - [Processing GEOMETRY OPTIMIZATION Calculation](#processing-geometry-optimization-calculation)
    - [Error Handing](#error-handing)
  - [Processing Cube File](#processing-cube-file)
  - [Processing PDOS File](#processing-pdos-file)
    - [Processing Single PDOS File](#processing-single-pdos-file)
    - [Quickplot of  PDOS Files in Single Point Energy Calculation](#quickplot-of--pdos-files-in-single-point-energy-calculation)

## Installation

```bash
pip install .
```



## Processing Output File

### Basick Usage
```python
from cp2kdata.output import Cp2kOutput
cp2k_output_file = "output_energy_force"
cp2koutput=Cp2kOutput(cp2k_output_file)
# show the brief summary on stdout
print(cp2koutput)
```

```stdout
Cp2k Output Summary

--------------------------------------

Cp2k Version       : 6.1

Run Type           : ENERGY_FORCE

Atom Numbers       : 30

Frame Numbers      : 1

Force in Output    : Yes

Stress in Output   : Yes

Element List       : Fe1  Fe2  O    

Element Numb       : 6    6    18   
--------------------------------------
```

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
### Error Handing
if cp2k output contains exceed execution time, the Cp2kOutput class won't read it.
Instead, to ignore the error, set 'ignore_error=True'
```python
cp2k_output_file = "output_geo_opt"
cp2koutput=Cp2kOutput(cp2k_output_file, ignore_error=True)
```
## Processing Cube File

```python
from cp2kdata.cube import Cp2kCube
cube_file = "xxx.cube"
mycube = Cp2kCube(cube_file)

# structure is include in cube file
# you can obtain ASE atoms from cube
stc = mycube.get_stc()
print(stc)

# get Planar average data without interpolation.
pav_x, pav = mycube.get_pav(axis="z", interpolate=False)
# get Planar average data  with interpolation. the number of interpolation point is 4096
pav_x, pav = mycube.get_pav(axis="z", interpolate=True)

l1 = 4.8 # length for first periodicity
l2 = 4.8 # length for second periodicity
ncov = 1 # set 1 if the system is slab-vacuum system.
ncov = 2 # set 2 if the system is interface.
# get Macro average data without interpolation of the original data.
mav_x, mav = mycube.get_mav(l1=l1, l2=l2, ncov=ncov, interpolate=False)
# get Macro average data with interpolation of the original data.
mav_x, mav = mycube.get_mav(l1=l1, l2=l2, ncov=ncov, interpolate=True)

# quick plot
mycube.quick_plot(axis="z", interpolate=False, output_dir="./")
```
The Planar Average and Macro Average results are benchmarked from MACROAVE used in 
[Siesta and Abinit](https://docs.siesta-project.org/projects/siesta/reference/macroave.html)
and shown in the following figures

![pav_plot](./figures/PAV_compare.png)
![mav_plot](./figures/MAV_compare.png)

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

