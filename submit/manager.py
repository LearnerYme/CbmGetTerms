r'''
    
    Cumulant Calculation Manage System
    Author: Yige HUANG

    Latest Revision: v3.0 (03.03.2024) - Yige Huang

    > With AnalysisTemplate framework, see: https://github.com/LearnerYme/AnalysisTemplate
    
    Revision: v2.0 (15.01.2024) - Yige Huang
    
    (for CBM analysis)
    
    Revision: v1.1 (14.09.2023) - Yige Huang

    > The multi-subtasks (for rapidity scan) are sharing the log file, so only the last task can work normally.
    > This bug is due to the difference between RCF and virgo's submitting system, and now it is fixed.

    Revision: v1.0 (11.09.2023) - Yige Huang

    > First version for CBM virgo server.
    > Based on manager system in RCF server v2.4.

'''


import sys
import os
from conf import Args, CutArgs
from yLog import yLog

main_patch = 3.0
mode = sys.argv[1]
assert(mode in ['sub', 'submit', 'mer', 'merge', 'run', 'calc', 'col', 'collect', 'clean', 'repo', 'report'])

if mode not in ['clean', 'repo', 'report']:
    # verifying rapidity scan validation
    nScan = len(CutArgs.task_tags)
    if not nScan == len(CutArgs.yMins) == len(CutArgs.yMaxs):
        raise Exception('[ERROR] The rapidity scan min and max should have a same length with task tags.')
    else:
        print(f'There will be {nScan} sub-jobs.')
        print(f'Rapidity scan min list: {CutArgs.yMins}')
        print(f'Rapidity scan max list: {CutArgs.yMaxs}')
        print(f'Rapidity scan task names: {CutArgs.task_tags}')

# submit mode
if (mode in ['sub', 'submit']):
    l = yLog('.submit.log')

    l.log(f'===Submit System for GetTerms===')
    l.log(f'Current configuration patch {Args.conf_patch} and manager patch number {main_patch}')
    l.log('Summary of configuration are listed below:')
    l.log(f'Number of files per job: {Args.nFilesPerJob}')
    l.log(f'Output directory:{Args.outDir}')
    l.log(f'File list: {Args.fileList}')
    l.log(f'Efficiency file path: {Args.eff_path}')
    l.log(f'Efficiency factor: {Args.eff_fac}')
    if Args.main_mode == 0:
        l.log('Main mode [0]: Deal with PhQMD simulation')
    elif Args.main_mode == 1:
        l.log('Main mode [1]: Deal with PhQMD+Geant simulation')
    elif Args.main_mode == 2:
        l.log('Main mode [2]: Deal with PhQMD+Geant simulation with RefMult3M (defined with PDG id)')
    else:
        raise Exception(f'[ERROR] Invalid main mode {Args.main_mode}')

    with open(Args.fileList) as f:
        flist = f.readlines()
    nFiles = len(flist)
    nFilesPerJob = Args.nFilesPerJob
    nJobs = nFiles // nFilesPerJob
    bonus = nFiles - nJobs * nFilesPerJob

    l.log(f'{nFiles} files in total, {nJobs} regular jobs with {nFilesPerJob} files to handle.')
    if bonus:
        l.log(f'Bonus job will manage {bonus} jobs.')

    l.log('Now preparing Job Directory and File Lists. May take few seconds.')
    outDir = Args.outDir
    if not os.path.exists(outDir):
        os.mkdir(outDir)

    for i in range(nJobs):
        if not os.path.exists(f'{outDir}/job{i}'):
            os.mkdir(f'{outDir}/job{i}')
            with open(f'{outDir}/job{i}/file.list', 'w') as f:
                for line in range(i * nFilesPerJob, (i+1) * nFilesPerJob):
                    f.write(flist[line])
    if bonus:
        if not os.path.exists(f'{outDir}/job{nJobs}'):
            os.mkdir(f'{outDir}/job{nJobs}')
            with open(f'{outDir}/job{nJobs}/file.list', 'w') as f:
                for line in range(nJobs * nFilesPerJob, nFiles):
                    f.write(flist[line])
    l.log('Done.')

    l.log('Now copying necessary files. May take few seconds.')
    if bonus:
        nJobs += 1
    
    # getTerms (exec): just symlink
    # getTerms.sh: change the path and the name
    # getTerms.cfg: generate one and symlink to jobs

    for item, ymin, ymax in zip(CutArgs.task_tags, CutArgs.yMins, CutArgs.yMaxs):
        with open(f'{item}.getTerms.cfg', 'w') as f:
            f.write(f'VARLIST\n')
            f.write(f'PT\t{CutArgs.ptMin}\t{CutArgs.ptMax}\n')
            f.write(f'YP\t{ymin}\t{ymax}\n')
            f.write(f'MASS2\t{CutArgs.m2Min}\t{CutArgs.m2Max}\n')
            # f.write(f'TOFHIGH\t{CutArgs.fUpperPars[0]}\t{CutArgs.fUpperPars[1]}\t{CutArgs.fUpperPars[2]}\n')
            # f.write(f'TOFLOW\t{CutArgs.fLowerPars[0]}\t{CutArgs.fLowerPars[1]}\t{CutArgs.fLowerPars[2]}\t{CutArgs.fLowerTrancated}\n')
            f.write(f'END')

    for i in range(nJobs):
        tdir = f'{outDir}/job{i}'

        # getTerms exec
        if not os.path.exists(f'{tdir}/AnalysisExec'):
            os.system(f'cp ../build/AnalysisExec {tdir}/AnalysisExec')

        for item in CutArgs.task_tags:
            # getTerms job shell
            os.system(f'cp run.sh {tdir}/{item}.run.sh')
            os.system(f'sed -i "s|__JOBNAMETAG__|{item}|g" {tdir}/{item}.run.sh')
            os.system(f'sed -i "s|__JOBID__|{i}|g" {tdir}/{item}.run.sh')
            os.system(f'sed -i "s|__EFF_PATH__|{Args.eff_path}|g" {tdir}/{item}.run.sh')
            os.system(f'sed -i "s|__EFF_FAC__|{Args.eff_fac}|g" {tdir}/{item}.run.sh')
            os.system(f'sed -i "s|__MAIN_MODE__|{Args.main_mode}|g" {tdir}/{item}.run.sh')

            # getTerms cfg file
            if os.path.exists(f'{tdir}/{item}.getTerms.cfg'):
                os.system(f'rm {tdir}/{item}.getTerms.cfg')
            os.symlink(f'{os.getcwd()}/{item}.getTerms.cfg', f'{tdir}/{item}.getTerms.cfg')

    l.log('Done.')

    l.log('Now submitting jobs.')
    for item in CutArgs.task_tags:
        for i in range(nJobs):
            tdir = f'{outDir}/job{i}'
            l.log(f' - Current {item}::job{i+1} / {nJobs}')
            os.system(f'cd {tdir} && sbatch {item}.run.sh')
    l.log('All submitted!')

# merge mode
if mode in ['mer', 'merge']:
    l = yLog('.merge.log')
    l.log(f'Current configuration patch {Args.conf_patch} and manager patch number {main_patch}')
    outDir = Args.outDir
    mergeDir = Args.mergeDir

    if not os.path.exists(outDir):
        raise Exception(f'Output directory {outDir} which does not exist.')

    if not os.path.exists(mergeDir):
        os.mkdir(mergeDir)

    # WE will need to find the task names,
    # for example, trad.y1.root, trad.y2.root, ... , pDist.root
    # taskNames = os.listdir(f'{outDir}/job0') # job 0 must exists, otherwise it is not submitted
    
    # Now we can directly use CutArgs.task_tags
    taskNames = []
    for item in CutArgs.task_tags:
        taskNames.append(f'{item}.root')
        taskNames.append(f'{item}.pDist.root')

    print('Here are the root files to be merged (not sorted):')
    for idx, item in enumerate(taskNames):
        l.log(f'Item {idx+1:03d} - {item}')

    for item in taskNames:
        srt = item[:-5]
        if not os.path.exists(f'{mergeDir}/{srt}'):
            os.mkdir(f'{mergeDir}/{srt}')
        os.system(f'cp merge.py {mergeDir}/{srt}')
        os.system(f'cp yLog.py {mergeDir}/{srt}')
        os.system(f'cp merge.sh {mergeDir}/{srt}/{item}.merge.sh')

        os.system(f'sed -i "s|__JOBNAMETAG__|{item}|g" {mergeDir}/{srt}/{item}.merge.sh')
        os.system(f'sed -i "s|__TASKNAME__|{item}|g" {mergeDir}/{srt}/{item}.merge.sh')
        os.system(f'sed -i "s|__OUTDIR__|{outDir}|g" {mergeDir}/{srt}/{item}.merge.sh')
        os.system(f'sed -i "s|__MERDIR__|{mergeDir}|g" {mergeDir}/{srt}/{item}.merge.sh')
        os.system(f'cd {mergeDir}/{srt} && sbatch {item}.merge.sh')
        l.log(f' - Current {item}')

    l.log('All submitted!')

# run mode
if mode in ['run', 'calc']:
    l = yLog('.calc.log')
    l.log(f'Current configuration patch {Args.conf_patch} and manager patch number {main_patch}')
    mergeDir = Args.mergeDir
    runDir = Args.runDir

    if not os.path.exists(mergeDir):
        raise Exception(f'Merge directory {mergeDir} which does not exist.')
    
    if not os.path.exists(runDir):
        os.mkdir(runDir)

    # taskNames = os.listdir(f'{mergeDir}')
    # taskNames = [item[:-5] for item in taskNames if item[-4:] == 'root' and item[:5] != 'pDist']
    taskNames = CutArgs.task_tags

    print('Here are the task names to be calculated (not sorted):')
    for idx, item in enumerate(taskNames):
        l.log(f'Item {idx+1:03d} - {item}')

    for item in taskNames:
        if not os.path.exists(f'{runDir}/{item}'):
            os.mkdir(f'{runDir}/{item}')
        if not os.path.exists(f'{runDir}/{item}/runCumulant'):
            os.symlink(Args.calc_exec, f'{runDir}/{item}/runCumulant')
        if os.path.exists(f'{runDir}/{item}/{item}.root'):
            os.remove(f'{runDir}/{item}/{item}.root')
        os.symlink(f'{mergeDir}/{item}.root', f'{runDir}/{item}/{item}.root')
        os.system(f'cp calc.sh {runDir}/{item}/{item}.calc.sh')
        os.system(f'sed -i "s|__TASKNAME__|{item}|g" {runDir}/{item}/{item}.calc.sh')
        if Args.main_mode == 1:
            os.system(f'sed -i "s|__MULTMODE__|0|g" {runDir}/{item}/{item}.calc.sh')
        elif Args.main_mode in [0, 2]:
            os.system(f'sed -i "s|__MULTMODE__|1|g" {runDir}/{item}/{item}.calc.sh')
        os.system(f'cd {runDir}/{item} && sbatch {item}.calc.sh')
        l.log(f' - Current {item}')
        
    l.log('All submitted!')

# collect mode
if mode in ['col', 'collect']:
    l = yLog('.collect.log')
    l.log(f'Current configuration patch {Args.conf_patch} and manager patch number {main_patch}')
    mergeDir = Args.mergeDir
    runDir = Args.runDir

    if not os.path.exists(mergeDir):
        raise Exception(f'Merge directory {mergeDir} which does not exist.')

    if not os.path.exists(runDir):
        raise Exception(f'Calculation directory {runDir} which does not exist.')
    
    taskNames = CutArgs.task_tags

    print('Here are the task names to be collected:')
    for idx, item in enumerate(taskNames):
        l.log(f'Item {idx+1:03d} - {item}')

    col = f'{Args.title}.coll'

    if os.path.exists(col):
        l.log(f'Already have {col} now removing it.')
        os.system(f'rm -rf {col}')
    
    os.mkdir(col)
    for item in taskNames:
        os.system(f'cp {mergeDir}/{item}.pDist.root {col}/')
        os.system(f'cp {runDir}/{item}/cum.{item}.root {col}/')
        os.system(f'cp {runDir}/{item}/cum.{item}.Graph.root {col}/')
    
    if os.path.exists(f'{col}.tgz'):
        l.log(f'Already have {col}.tgz now removing it.')
        os.remove(f'{col}.tgz')
    os.system(f'tar -zcvf {col}.tgz {col}/')
    l.log(f'All done. See {col} and {col}.tgz')

# clean mode
if mode == 'clean':
    l = yLog('.clean.log')
    l.log(f'Current configuration patch {Args.conf_patch} and manager patch number {main_patch}')
    if len(sys.argv) != 3:
        l.log(f'Clean All: It is dangerous! This function is forbiden!')
    else:
        clcmd = sys.argv[2]
        if clcmd not in ['cfg', 'out', 'merge', 'run', 'calc']:
            raise Exception(f'Clean Mode support the following command: cfg out merge run calc. Received: {clcmd}')
        elif clcmd == 'cfg':
            files = os.listdir()
            nrm = 0
            for item in files:
                if item[-13:] == '.getTerms.cfg':
                    l.log(f'Removing: {item}')
                    os.remove(item)
                    nrm += 1
            l.log(f'Removed {nrm} generated .cfg files.')
        elif clcmd == 'out':
            l.log(f'Need safe word, please input CONFIRM and continue:')
            k = input()
            if k == 'CONFIRM':
                outDir = Args.outDir
                l.log(f'Now we are trying to clean {outDir}.')
                os.system(f'rm -rf {outDir}')
                l.log(f'Removed.')
            else:
                l.log(f'Safe word was not accepted, canceled.')
        elif clcmd == 'merge':
            l.log(f'Need safe word, please input CONFIRM and continue:')
            k = input()
            if k == 'CONFIRM':
                mergeDir = Args.mergeDir
                l.log(f'Now we are trying to clean {mergeDir}.')
                os.system(f'rm -rf {mergeDir}')
                l.log(f'Removed.')
            else:
                l.log(f'Safe word was not accepted, canceled.')
        elif clcmd in ['run', 'calc']:
            l.log(f'Need safe word, please input CONFIRM and continue:')
            k = input()
            if k == 'CONFIRM':
                runDir = Args.runDir
                l.log(f'Now we are trying to clean {runDir}.')
                os.system(f'rm -rf {runDir}')
                l.log(f'Removed.')
            else:
                l.log(f'Safe word was not accepted, canceled.')
        else:
            l.log('Nothing happend. But I don\'t think you can see this in log file.')

# report mode
if mode in ['repo', 'report']:
    l = yLog('.report.log')
    l.log(f'Current configuration patch {Args.conf_patch} and manager patch number {main_patch}')
    ntask = len(CutArgs.task_tags)
    l.log('Here is the Report of this workshop:')

    # get the number of jobs
    with open(Args.fileList) as f:
        flist = f.readlines()
    nFiles = len(flist)
    nFilesPerJob = Args.nFilesPerJob
    nJobs = nFiles // nFilesPerJob
    bonus = nFiles - nJobs * nFilesPerJob
    if bonus:
        nJobs += 1
    
    # show reports
    l.log(f'<======{Args.title}======>')
    
    l.log(f'====== General Information ======')
    l.log(f'[T] pT cut: {CutArgs.ptMin} - {CutArgs.ptMax}')
    l.log(f'[T] Mass square cut lower limit: {CutArgs.m2Min}')
    l.log(f'[T] Mass square cut upper limit.: {CutArgs.m2Max}')
    # l.log(f'[T] Mass square cut upper pars.: {CutArgs.fUpperPars}')
    # l.log(f'[T] Mass square cut lower pars.: {CutArgs.fLowerPars}')
    # l.log(f'[T] Mass square cut lower trancated at: {CutArgs.fLowerTrancated}')
    l.log(f'Rapidity scan has {ntask} tasks.')
    for idx, item in enumerate(zip(CutArgs.task_tags, CutArgs.yMins, CutArgs.yMaxs)):
        tag, ymin, ymax = item
        l.log(f'Item {idx+1:03d} / {ntask} - {tag}: {ymin:.2f} - {ymax:.2f}')
    
    if os.path.exists(Args.outDir):
        l.log(f'====== As for getTerms ===== [E]')
        l.log(f'Jobs are here: {Args.outDir}')
        l.log('The directory exists, which means we are done or doing this step.')
    else:
        l.log(f'====== As for getTerms ===== [D]')
        l.log(f'Jobs are here: {Args.outDir}')
        l.log('The directory does not exist, which means it has not got started or is removed already.')
    l.log(f'File list is: {Args.fileList} ({nFiles} files).')
    l.log(f'{nJobs} jobs are dispatched for processing {nFilesPerJob} files.')
    if bonus:
        l.log(f'Among them, there is a bonus job which will process {bonus} files.')
    else:
        l.log(f'No bonus job for this time.')
    l.log(f'The efficiency path is: {Args.eff_path}')

    if os.path.exists(Args.mergeDir):
        l.log(f'====== As for merge ====== [E]')
        l.log(f'Jobs are here: {Args.mergeDir}')
        l.log('The directory exists, which means we are done or doing this step.')
    else:
        l.log(f'====== As for merge ====== [D]')
        l.log(f'Jobs are here: {Args.mergeDir}')
        l.log('The directory does not exist, which means it has not got started or is removed already.')
    
    if os.path.exists(Args.runDir):
        l.log(f'====== As for cumulant calculation ====== [E]')
        l.log(f'Jobs are here: {Args.runDir}')
        l.log('The directory exists, which means we are done or doing this step.')
    else:
        l.log(f'====== As for cumulant calculation ====== [D]')
        l.log(f'Jobs are here: {Args.runDir}')
        l.log('The directory does not exist, which means it has not got started or is removed already.')
    l.log(f'The executable file: {Args.calc_exec}')
    
    l.log('This is the end of report.')
