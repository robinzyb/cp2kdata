# Manipulate CP2K Output/Log Files

## Basick Usage
One can use `Cp2kOutput` class to parse cp2k `output file`, which is the standard output from cp2k code. Depending on run types, required files may be more than a standard output. For example, if you parse `md` outputs, you may ask to provide additional `Project-1.ener`, `Project-pos-1.xyz`, and `Project-frc-1.xyz` files to obtain `energies`, `position`, and `forces` information. Detail usages are provided in the following subsections.

```python
from cp2kdata import Cp2kOutput
cp2k_output_file = "cp2k_output"
cp2koutput = Cp2kOutput(cp2k_output_file, path_prefix=".")
# path_prefix is the directory where the cp2k_output is
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

## Parse ENERGY_FORCE Outputs
```python
from cp2kdata import Cp2kOutput
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

## Parse GEO_OPT Outputs
```python
from cp2kdata import Cp2kOutput
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

## Parse MD outputs
On parsing MD outputs, you can choose parse *with* or *without* standard outputs. Three additional files, `Project-1.ener`, `Project-pos-1.xyz`, and `Project-frc-1.xyz` files, are required to obtain `energies`, `position`, and `forces` information. 

If you parse with standard outputs, `Cp2kOutput` can collect full information from outputs. In specific, cell information and kind symbols can be obtained. 

```python
from cp2kdata import Cp2kOutput
cp2k_output_file = "output_md"
cp2koutput=Cp2kOutput(cp2k_output_file)
```

Alternatively, you may parse without standard outputs. Consequently, you will loss the `cell` and `atomic kind` infromations. When parsing without standard outputs, you must manually set the optional argument `run_type` as `md`, otherwise it will raise error.

```python
from cp2kdata import Cp2kOutput
cp2k_output_file = "output_md"
cp2koutput=Cp2kOutput(run_type="md")
```