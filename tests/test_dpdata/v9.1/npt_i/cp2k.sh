#!/bin/bash
#SBATCH -J jiqun
#SBATCH -p lma
#SBATCH -n 28
#SBATCH -o %j.log
#SBATCH -e %j.log


module load cp2k/9.1

srun cp2k.popt md.inp &>log
