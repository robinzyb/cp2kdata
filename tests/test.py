from cp2kdata.output import Cp2kOutput
#x=Cp2kOutput("output_energy_force")
x=Cp2kOutput("output_geo_opt")
#x=Cp2kOutput("output")
y=Cp2kOutput("output_aimd")
#print(x.get_geo_opt_info())
#print(x.get_version_string())
#print(x.get_run_type())

#print(y.get_run_type())
#print(x.get_atomic_forces())
##print(x.get_atomic_forces().shape)

print(y.get_mulliken_pop_list())
print(x.get_mulliken_pop_list())
#
#print(x.get_hirshfeld_pop_list()[0])


#print(x.get_atomic_forces_list().shape)
#print(x.get_hirshfeld_pop())

#print(x.get_dft_plus_u_occ())
