import os
import sys
from yLog import yLog

taskName = sys.argv[1]
outDir = sys.argv[2]
mergeDir = sys.argv[3]

# add an mode option, mode 0 using traditional merge:
#   - root file one by one
#  and mode 1 using global:
#   - just hadd all
if len(sys.argv) == 4: 
    mode = 1
else:
    mode = int(sys.argv[4])

l = yLog(f'.{taskName}.merge.log')

l.log(f'Task name: {taskName}')
l.log(f'Output directory: {outDir}')
l.log(f'Merge directory: {mergeDir}')
if mode == 0:
    l.log(f'One-by-one mode.')
elif mode == 1:
    l.log(f'Global mode.')
else:
    l.log(f'Invalid mode.')
    exit()

lists = os.listdir(outDir)
lists = [f'{outDir}/{item}/{taskName}' for item in lists]

n = len(lists)

if mode == 0:
    baseFile = lists.pop(0)
    l.log(f'Now hadd 1 / {n} : {baseFile}')
    os.system(f'cp {baseFile} {mergeDir}/tmp.{taskName}')
    for idx, item in enumerate(lists):
        l.log(f'Now hadd {idx + 2} / {n} : {item}')
        os.system(f'hadd -f {mergeDir}/{taskName} {item} {mergeDir}/tmp.{taskName}')
        os.system(f'mv {mergeDir}/{taskName} {mergeDir}/tmp.{taskName}')
    os.system(f'mv {mergeDir}/tmp.{taskName} {mergeDir}/{taskName}')
if mode == 1:
    os.system(f'hadd -f {mergeDir}/{taskName} {outDir}/job*/{taskName}')

l.log('All done.')
