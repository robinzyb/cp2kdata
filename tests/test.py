from cp2kdata.output import Cp2kOutput

output_file = "cp2k_output_duplicate_header"
with open(output_file, 'r') as fp:
    header_idx = []
    for idx, ii in enumerate(fp):
        if 'Multiplication driver' in ii:
            header_idx.append(idx)

    all_lines = []
    for idx, ii in enumerate(fp):
        if idx > header_idx[-1]:
            all_lines.append(ii)
    
    print("".join(all_lines))

# cp2koutput=Cp2kOutput("output_geo_opt")
#x = Cp2kOutput("output_geo_opt")
# print(x.get_init_atomic_coordinates())
# print(x.get_init_atomic_coordinates().shape)
# print(x.get_atom_kinds_list())
# print(cp2koutput.get_version_string())
# get the run type
# print(cp2koutput.get_run_type())
# symbols with true element
# print(cp2koutput.get_chemical_symbols())
# symbols with your set in input
# print(cp2koutput.get_chemical_symbols_fake())
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
