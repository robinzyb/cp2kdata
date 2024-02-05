# CP2KData Plugin for dpdata

`CP2KData` supports a plugin for `dpdata`. When you install `CP2KData` using `pip`, the plugin for `dpdata` is automatically installed as well.

For instructions on how to use `dpdata`, please refer to the official repository: https://github.com/deepmodeling/dpdata.

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

2. `cp2kdata/md` format for parsing `MD` outputs.

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

These examples demonstrate how to use `Cp2kData` with `dpdata` to parse and work with data from CP2K simulations in the specified formats.
