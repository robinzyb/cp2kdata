# CP2KData plugin for dpdata

`CP2KData` supports a plugin for `dpdata`. When you install `CP2KData` using `pip`, the plugin for `dpdata` is automatically installed as well.

For instructions on how to use `dpdata`, please refer to the official repository: https://github.com/deepmodeling/dpdata.

In the following, we provide two exmples that demonstrate how to use `Cp2kData` with `dpdata` to parse data from CP2K simulations in specified formats.

## Parse Energy_Force
Currently, `CP2KData` supports two formats for use with `dpdata`:

1. `cp2kdata/e_f` format for parsing `ENERGY_FORCE` outputs.

   Example for parsing `ENERGY_FORCE` outputs:
   ```python
   import dpdata

   dp = dpdata.LabeledSystem("cp2k_e_f_output", fmt="cp2kdata/e_f")
   print(dp)
   ```

   Recommended Setups in the input of  `ENERGY_FORCE` calculation.
   ```shell
   &FORCE_EVAL
      # if stress tensor is not need to computed, comment out the below line.
      STRESS_TENSOR ANALYTICAL
      &PRINT
         &FORCES ON
         &END FORCES
         # if stress tensor is not need to computed, comment out the below line
         &STRESS_TENSOR ON
         # if stress tensor is not need to computed, comment out the below line
         &END STRESS_TENSOR
      &END PRINT
   &END FORCE_EVAL
   ```

   Single-point energy calculations are usually distributed across multiple folders. We need to loop through these folders. Here, I provide a script that can perform this task.
   ```python
   import dpdata
   from pathlib import Path


   system_list = [
      "system_1",
      "system_2"
   ]
   prefix_wkdir = "stc_"
   cp2k_log_name = "output"

   root=Path("./")

   # make a folder to store the datasets
   datadir=root/"data_set_new"
   datadir.mkdir(exist_ok=True, parents=True)

   for system in system_list:
      wkdirs = root/f"{system}"
      wkdirs = list(wkdirs.glob(f"{prefix_wkdir}*"))
      wkdirs.sort()

      dp = None
      for wkdir in wkdirs:
         print(f"process {wkdir}")
         if dp == None:
               dp = dpdata.LabeledSystem(wkdir/cp2k_log_name, fmt="cp2kdata/e_f")
         else:
               dp += dpdata.LabeledSystem(wkdir/cp2k_log_name, fmt="cp2kdata/e_f")

      dp.to_deepmd_npy(datadir/system)

   ```

## Parse MD
### MD including CP2K output/log files
  `cp2kdata/md` format for parsing `MD` outputs.

   Example for parsing `MD` outputs:
   ```python
   import dpdata

   cp2kmd_dir = "."
   cp2kmd_output_name = "output"
   dp = dpdata.LabeledSystem(cp2kmd_dir, cp2k_output_name=cp2kmd_output_name, fmt="cp2kdata/md")
   print(dp)
   ```
   Recommended Setups in the input of  `MD` calculation.

   ```shell
   @SET frequency 100
   &FORCE_EVAL
      # if stress tensor is not need to computed, comment out the below line.
      STRESS_TENSOR ANALYTICAL
      &PRINT
         # if stress tensor is not need to computed, comment out the below line
         &STRESS_TENSOR ON
         # if stress tensor is not need to computed, comment out the below line
            &EACH
         # if stress tensor is not need to computed, comment out the below line
               MD ${frequency}
         # if stress tensor is not need to computed, comment out the below line
            &END EACH
         # if stress tensor is not need to computed, comment out the below line
         &END STRESS_TENSOR
      &END PRINT
   &END FORCE_EVAL
   &MOTION
      &MD
         &PRINT
            &ENERGY
               &EACH
                  MD ${frequency}
               &END EACH
            &END ENERGY
         &END PRINT
      &END MD
      &PRINT
         &CELL
            &EACH
               MD ${frequency}
            &END EACH
         &END CELL
         &FORCES
            &EACH
               MD ${frequency}
            &END EACH
         &END FORCES
         &TRAJECTORY
            &EACH
               MD ${frequency}
            &END EACH
         &END TRAJECTORY
      &END PRINT
   &END MOTION
   ```

### MD without CP2K output/log files
   In some cases, users only keep `*-pos-*.xyz` and `*-frc-*.xyz` files. To convert the CP2K files into dpdata, users must explicitly tells dpdata the cell and ensemble information.

   ```python
   import dpdata
   import numpy as np

   cp2kmd_dir = "./test/"
   cp2kmd_output_name = None

   cells = np.array([[8.66,0,0],
                    [0,8.66,0],
                    [0,0,22.83]])
   dp = dpdata.LabeledSystem(cp2kmd_dir, cp2k_output_name=cp2kmd_output_name, cells=cells, ensemble_type="NVT", fmt="cp2kdata/md")
   ```

### MD missing restart information in header
   In some cases, CP2K md simulations are restarted from `-1.restart` file in which the initial structure will not be evaluated again.
   Therefore, the initial cell information should not be parsed again. Otherwise, the number of frames for cells is inconsistent with those for `poses`, `forces`, and `energies`.
   Cp2kdata can automatically check whether the simulations are restarted or not through the header information of output:
   ```
    *******************************************************************************
    *                            RESTART INFORMATION                              *
    *******************************************************************************
    *                                                                             *
    *    RESTART FILE NAME: bivo4-water-1.restart                                 *
    *                                                                             *
    * RESTARTED QUANTITIES:                                                       *
    *                       CELL                                                  *
    *                       COORDINATES                                           *
    *                       RANDOM NUMBER GENERATOR                               *
    *                       VELOCITIES                                            *
    *                       MD COUNTERS                                           *
    *                       MD AVERAGES                                           *
    *                       PARTICLE THERMOSTAT                                   *
    *                       REAL TIME PROPAGATION                                 *
    *                       PINT BEAD POSITIONS                                   *
    *                       PINT BEAD VELOCITIES                                  *
    *                       PINT NOSE THERMOSTAT                                  *
    *                       PINT GLE THERMOSTAT                                   *
    *                       HELIUM BEAD POSITIONS                                 *
    *                       HELIUM PERMUTATION STATE                              *
    *                       HELIUM FORCES ON SOLUTE                               *
    *                       HELIUM RNG STATE                                      *
    *******************************************************************************
   ```
   if the simulations are restarted using:
   ```cp2k
   &EXT_RESTART
      RESTART_FILE_NAME Li-LiFSI-DME-1-2-1.restart
   &END EXT_RESTART
   ```
   In case your restarted output doesn't have the above header, you can explicitly tell the cp2kdata/dpdata by setting `restart=True`,
   ```python
   # restart = True in case the output doesn't contains header
   dp = dpdata.LabeledSystem(cp2kmd_dir, cp2k_output_name=cp2kmd_output_name, fmt="cp2kdata/md", restart=True)
   ```

