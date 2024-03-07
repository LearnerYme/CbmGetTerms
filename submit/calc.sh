#!/bin/bash

#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --output=.__TASKNAME__.calc.out
#SBATCH --error=.__TASKNAME__.calc.err
#SBATCH --job-name=__TASKNAME__

./runCumulant __TASKNAME__ __MULTMODE__

