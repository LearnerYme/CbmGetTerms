#/bin/bash

tpath=/lustre/hades/user/yige/4p9/cum/240115/corr/out
njobs=67

for i in $(seq 0 $njobs)
do
    for x in 0 2 4 6 8
    do
        cd $tpath/job$i && sbatch y0p$x.run.sh
    done
done

echo "all done"