from cp2kdata.output import Cp2kOutput
#x=Cp2kOutput("cp2k_output")
#x=Cp2kOutput("output")
x=Cp2kOutput("cp2k.log")
#print(x.get_version_string())
#print(x.get_run_type())
#print(x.get_atomic_forces())
##print(x.get_atomic_forces().shape)
#print(x.get_mulliken_pop())
#print(x.get_hirshfeld_pop())

print(x.get_dft_plus_u_occ())
