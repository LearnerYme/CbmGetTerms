class Args:
    conf_patch = 3.0
    nFilesPerJob = 30
    lusterDir = '/lustre/hades/user/yige/4p9/x/cum/240303/corr'
    outDir = f'{lusterDir}/out'
    mergeDir = f'{lusterDir}/merge'
    runDir = f'{lusterDir}/run'
    fileList = '/u/yige/DataAnalysis/cbm/4p9/0GetList/full.file.list'
    eff_path = '/u/yige/DataAnalysis/cbm/4p9/xGeneration/x2CalcEff/Efficiency.root'
    eff_fac = 1.0
    main_mode = 1.0 # 0 -> PhQMD, 1 -> rec., 2 -> rec. with RefMult3M
    calc_exec = '/u/yige/DataAnalysis/cbm/CumulantCalculation/runCumulant'
    title = 'corr'

class CutArgs:
    ptMin = 0.4
    ptMax = 2.0
    # With hard cut
    m2Min = 0.6
    m2Max = 1.2
    yMins = [
        -0.4, -0.4, -0.4, -0.4, -0.4
    ]
    yMaxs = [
        0.0, 0.2, 0.4, 0.6, 0.8
    ]
    task_tags = [
        'y0p0',
        'y0p2',
        'y0p4',
        'y0p6',
        'y0p8',
    ]

    # With momentum-dependent mass cut
    # fLowerPars = [0.780239, 0.0342841, -0.0218734]
    # fUpperPars = [0.930886, -0.0150339, 0.0168854]
    # fLowerTrancated = 4.5
