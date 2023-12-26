# CP2KData


[![Python package](https://github.com/robinzyb/cp2kdata/actions/workflows/ci.yml/badge.svg)](https://github.com/robinzyb/cp2kdata/actions/workflows/ci.yml)[![Coverage Status](https://coveralls.io/repos/github/robinzyb/cp2kdata/badge.svg)](https://coveralls.io/github/robinzyb/cp2kdata)
![pythonv](https://img.shields.io/pypi/pyversions/cp2kdata)
![pypiv](https://img.shields.io/pypi/v/cp2kdata)
![PyPI - pip install](https://img.shields.io/pypi/dm/cp2kdata?logo=pypi&label=pip%20install)

Python Package to postprocess cp2k data, including cube, pdos, output files


# Installation
## From pip
```bash
pip install cp2kdata
```

## From source
One can download the source code of cp2kdata by
```bash
git clone https://github.com/robinzyb/cp2kdata.git cp2kdata
```
then use `pip` to install the module from source

```bash
cd cp2kdata
pip install .
```

# Manipulate CP2K Files
- [Manipulate CP2K Output/Log Files](./docs/output.md)
- [Manipulate CP2K Cube Files](./docs/cube/README.md)
- [Manipulate CP2K Pdos Files](./docs/pdos/README.md)

# Additional Features
- [Plug in for dpdata](./docs/dpdata_plugin.md)

# Feature Request
Any advice is welcome. If you would like to request a new feature, please open an issue in github and upload example input and output files.






