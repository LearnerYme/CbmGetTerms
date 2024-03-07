#!/bin/bash

#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --output=.__JOBNAMETAG__.__JOBID__.out
#SBATCH --error=.__JOBNAMETAG__.__JOBID__.err
#SBATCH --job-name=__JOBNAMETAG__.__JOBID__

./AnalysisExec __EFF_PATH__ __JOBNAMETAG__ __EFF_FAC__ __MAIN_MODE__