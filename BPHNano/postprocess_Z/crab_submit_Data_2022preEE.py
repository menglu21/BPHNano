from WMCore.Configuration import Configuration

config = Configuration()

config.section_("General")
config.General.requestName = 'BNano_parking0_C'
config.General.transferLogs = True

config.section_("JobType")
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = "run_data_Run3Summer22.py"
#config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script_data.sh'
config.JobType.scriptArgs = []
config.JobType.inputFiles = ['postproc_data.py', "run_data_Run3Summer22.py", "crab_script_data.sh"]
config.JobType.outputFiles = ['out_step1_Skim.root']

config.section_("Data")
config.Data.inputDataset = '/ParkingDoubleMuonLowMass0/Run2022C-10Dec2022-v2/MINIAOD'
config.Data.inputDBS = 'global'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 400000 # events
config.JobType.maxMemoryMB = 4000  ## 2500*4
config.Data.publication = False
config.JobType.numCores = 2
config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json'
config.Data.outLFNDirBase = '/store/user/melu/Zraredecay/'

config.section_("Site")
config.Site.storageSite = "T2_CH_CERN"
