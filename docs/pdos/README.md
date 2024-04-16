# Manipulate CP2K Pdos Files

## Recommended Setups of CP2K inputs for Writing CP2K Pdos files

### Normal Pdos for Each Type of Elements
Under the `DFT/PRINT/PDOS` Section

```cp2k

&PDOS
    COMPONENTS
    NLUMO -1
    ADD_LAST  NUMERIC
    COMMON_ITERATION_LEVELS 0
    APPEND T
&END PDOS
```

### Ldos: Pdos for Selected Atoms
```cp2k
&PDOS
    COMPONENTS
    NLUMO -1
    ADD_LAST  NUMERIC
    COMMON_ITERATION_LEVELS 0
    APPEND T
    &LODS
        LIST 5 6 7 8
    &END LDOS
&END PDOS
```

## Processing Single PDOS File

```python
from cp2kdata import Cp2kPdos
dosfile = "Universality-ALPHA_k2-1_50.pdos"
mypdos = Cp2kPdos(dosfile)
dos, ener = mypdos.get_dos(sigma=1, dos_type="total")
```

If DOS is parsed from LDOS files, `dos_type=custom` is preferred, which can be used together with `usecols`. `usecols` accepts tuple with `int` elements. For example, `usecols=(3, 4, 5)`

```python
dosfile = "water-list1-1_0.pdos
mypdos = Cp2kPdos(dosfile)
dos, ener = mypdos.get_dos(dos_type='custom', usecols=(3, 4, 5))
```



## Quickplot of  PDOS Files in Single Point Energy Calculation

```python
from cp2kdata.pdos import quick_plot_uks, quick_plot_rks
Calculation_dir = "./"
# if uks calculation use this
quick_plot_uks(Calculation_dir)
# if rks calculation use this
quick_plot_rks(Calculation_dir)
```