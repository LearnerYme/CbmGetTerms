#!/bin/bash

#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --output=.__JOBNAMETAG__.merge.out
#SBATCH --error=.__JOBNAMETAG__.merge.err
#SBATCH --job-name=__JOBNAMETAG__

date
echo "Now start!"

python3 merge.py __TASKNAME__ __OUTDIR__ __MERDIR__ 1

date
echo "It's end!"
