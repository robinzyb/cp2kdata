# Manipulate CP2K Pdos Files

## Processing Single PDOS File

```python
from cp2kdata import Cp2kPdos
dosfile = "Universality-ALPHA_k2-1_50.pdos"
mypdos = Cp2kPdos(dosfile)
dos, ener = mypdos.get_dos()
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