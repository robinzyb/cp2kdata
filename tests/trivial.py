from cp2kdata.output import Cp2kOutput
#cp2koutput=Cp2kOutput("v6.1/duplicate_header")
#print(cp2koutput)
#print(cp2koutput.get_init_atomic_coordinates().shape)
#print(cp2koutput.get_geo_opt_info())
#cp2koutput=Cp2kOutput("v7.1/output-GEO-CG", ignore_error=True)
#cp2koutput=Cp2kOutput("v7.1/exceed_wall_time", ignore_error=True)
cp2koutput=Cp2kOutput("test_energy_force/v6.1/normal/output")

print(cp2koutput.get_init_cell())
print(cp2koutput.get_atom_num())
# get the version of cp2k
print(cp2koutput.get_version_string())
# get the run type
print(cp2koutput.get_run_type())
# symbols with true element
print(cp2koutput.get_chemical_symbols())
# symbols with your set in input
print(cp2koutput.get_atomic_forces_list())
print(cp2koutput.get_init_atomic_coordinates())
print(cp2koutput.get_chemical_symbols_fake())
print(cp2koutput.get_stress_tensor_list())
print(cp2koutput)
#print(cp2koutput.get_geo_opt_info())
#print(cp2koutput.get_geo_opt_info_plot())
#print(cp2koutput.get_atomic_kind())
#print(cp2koutput.get_force_status())
#print(cp2koutput.get_stress_tensor_list())
#cp2koutput = Cp2kOutput("v7.1/exceed_wall_time")
#print(cp2koutput.get_init_atomic_coordinates())
#print(cp2koutput)
# print(x.get_init_atomic_coordinates().shape)
# print(x.get_atom_kinds_list())
# print(cp2koutput.get_version_string())
# get the run type
# print(cp2koutput.get_run_type())
# symbols with true element
#print(cp2koutput.get_chemical_symbols())
# symbols with your set in input
#print(cp2koutput.get_chemical_symbols_fake())
# get the geometry optimization information
# print(cp2koutput.get_geo_opt_info())
# quick plot of geometry optimization information
# print(cp2koutput.get_geo_opt_info_plot())
# print(x.get_atomic_kind())
# print(x.get_chemical_symbols())
# print(x.get_chemical_symbols_fake())
# print(len(x.get_energies_list()))
# x=Cp2kOutput("output")
# y=Cp2kOutput("output_aimd")

# print(x.get_geo_opt_info())
# print(x.get_version_string())
# print(x.get_run_type())

# print(y.get_run_type())
# print(x.get_atomic_forces())
# print(x.get_atomic_forces().shape)

# print(y.get_mulliken_pop_list())
# print(x.get_mulliken_pop_list())
#
# print(x.get_hirshfeld_pop_list()[0])


# print(x.get_atomic_forces_list().shape)
# print(x.get_hirshfeld_pop())

# print(x.get_dft_plus_u_occ())
