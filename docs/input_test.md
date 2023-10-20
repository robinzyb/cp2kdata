# Generate Standard Test Inputs
One can use command line tools to generate standard test input with provided template `input.inp` and other files.
```bash
# generate cutoff test files
cp2kdata gen cutoff <template input> <a list of other neccessary files> -crange <cutoff range: min, max, step> --scf_converge <whether scf converge>

# example
cp2kdata gen cutoff input.inp coord.xyz cp2k.lsf -crange 100 800 100 --scf_converge True

# generate basis test files
cp2kdata gen basis <template input> <a list of other neccessary files> -e <test element> -sr <whether test short range basis>

# example
cp2kdata gen basis input.inp coord.xyz cp2k.lsf -e Fe -sr True

# generate Hubbard U test files
cp2kdata gen hubbardu <template input> <a list of other neccessary files> -ur u <test value: min, max, step> -e <test element> -orb <test orbital>  
# example
cp2kdata gen hubbardu input.inp coord.xyz cp2k.lsf -ur 0 8.1 1 -e Fe -orb d  
```
# Plot Standard Test Output
Once you have completed the tests mentioned above, you can easily generate plots of the results using the following commands:

- To plot the cutoff data, use: `cp2kdata plot cutoff`
- To plot the basis data, use: `cp2kdata plot basis`
- To plot the Hubbard U data, use: `cp2kdata plot hubbardu`