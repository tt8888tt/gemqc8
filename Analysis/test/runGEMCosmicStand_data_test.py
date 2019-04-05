# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: SingleMuPt100_cfi -s GEN,SIM,DIGI,L1,DIGI2RAW,RAW2DIGI,L1Reco,RECO --conditions auto:run2_mc --magField 38T_PostLS1 --datatier GEN-SIM --geometry GEMCosmicStand --eventcontent FEVTDEBUGHLT --era phase2_muon -n 100 --fileout out_reco.root
import datetime
print datetime.datetime.now()
import FWCore.ParameterSet.Config as cms
import configureRun_cfi as runConfig

# options
import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing('analysis')

options.register("runNum",1,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Run number")
                 
options.register("eventsPerJob",500,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "The number of events (in each file)")
                 
options.register("idxJob","-1",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "The index of this root file")
options.register('mps',
                 '',
                 VarParsing.VarParsing.multiplicity.list,
                 VarParsing.VarParsing.varType.int,
                 "List of MPs to process")


options.parseArguments()

# The superchambers in the 15 slots
SuperChType = runConfig.StandConfiguration

print(SuperChType)

# Calculation of SuperChSeedingLayers from SuperChType
SuperChSeedingLayers = []

for i in range (0,30):
	SuperChSeedingLayers.append(0)

for j in range (0,3):
	for i in range (5*j,5*(j+1)):
		if (SuperChType[i]!='0'):
			SuperChSeedingLayers[i*2]=1
			SuperChSeedingLayers[i*2+1]=3
			break
	for i in range (5*(j+1)-1,5*j-1,-1):
		if (SuperChType[i]!='0'):
			SuperChSeedingLayers[i*2]=4
			SuperChSeedingLayers[i*2+1]=2
			break
			
print(SuperChSeedingLayers)

from Configuration.StandardSequences.Eras import eras

process = cms.Process('RECO',eras.phase2_muon)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('gemqc8.Analysis.GeometryGEMCosmicStand_cff')
process.load('Configuration.StandardSequences.MagneticField_0T_cff')

process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.RecoSim_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
#process.load('Configuration.StandardSequences.Digi_cff')
#process.load('Configuration.StandardSequences.Reconstruction_cff')
#process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# DEFINITION OF THE SUPERCHAMBERS INSIDE THE STAND
for i in xrange(len(SuperChType)):
    column_row = '_c%d_r%d' % ((i/5)+1, i%5+1)
    if SuperChType[i]=='L' : size = 'L'
    if SuperChType[i]=='S' : size = 'S'
    if SuperChType[i]!='0' :
    	geomFile = 'gemqc8/Analysis/data/gem11'+size+column_row+'.xml'
    	print(geomFile)
    if SuperChType[i]!='0' :
    	process.XMLIdealGeometryESSource.geomXMLFiles.append(geomFile)
    	print('-> Appended')

# Config importation & settings
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.eventsPerJob))
nIdxJob = int(options.idxJob)
strOutput = "out_reco_MC.root" if nIdxJob >= 0 else runConfig.OutputFileName
if nIdxJob < 0: nIdxJob = 0


import os
fpath =  "/cms/scratch/hyunyong/QC8/"
# Input source
process.source = cms.Source(
    "GEMLocalModeDataSource",
    #fileNames = cms.untracked.vstring (options.inputFiles),
    fileNames = cms.untracked.vstring ([fpath+x for x in os.listdir(fpath) if x.endswith(".dat")]),
    skipEvents=cms.untracked.uint32(0),
    fedId = cms.untracked.int32( 1472 ),  # which fedID to assign
    hasFerolHeader = cms.untracked.bool(False),
    runNumber = cms.untracked.int32( 35),
)
process.options = cms.untracked.PSet(
    SkipEvent = cms.untracked.vstring('ProductNotFound')
)
############## DB file #################
from CondCore.CondDB.CondDB_cfi import *
CondDB.DBParameters.authenticationPath = cms.untracked.string('/afs/cern.ch/cms/DB/conddb')
CondDB.connect = cms.string('sqlite_fip:gemqc8/Analysis/data/GEMeMap.db')

process.GEMCabling = cms.ESSource("PoolDBESSource",
    CondDB,
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('GEMeMapRcd'),
        tag = cms.string('GEMeMap_v3')
    )),
)
####################################

process.MessageLogger.cerr.FwkReport.reportEvery = 1000
# validation event filter
process.load('EventFilter.L1TRawToDigi.validationEventFilter_cfi')

process.load('EventFilter.L1TRawToDigi.tmtFilter_cfi')
process.tmtFilter.mpList = cms.untracked.vint32(options.mps)

# Additional output definition
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

# Cosmic Muon generator
process.load('RecoMuon.TrackingTools.MuonServiceProxy_cff')
process.MuonServiceProxy.ServiceParameters.Propagators.append('StraightLinePropagator')
process.load('EventFilter.GEMRawToDigi.muonGEMDigis_cfi')
process.muonGEMDigis.InputLabel = cms.InputTag("source","gemLocalModeDataSource")
process.muonGEMDigis.useDBEMap = True
process.muonGEMDigis.unPackStatusDigis = True


process.load('RecoLocalMuon.GEMRecHit.gemRecHits_cfi')

process.gemRecHits = cms.EDProducer("GEMRecHitProducer",
    recAlgoConfig = cms.PSet(),
    recAlgo = cms.string('GEMRecHitStandardAlgo'),
    gemDigiLabel = cms.InputTag("muonGEMDigis"),
)

process.path = cms.Path(
    process.muonGEMDigis
    +process.gemRecHits
)

process.path.remove(process.tmtFilter)


process.output = cms.OutputModule(
    "PoolOutputModule",
    outputCommands = cms.untracked.vstring("keep *"),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('path')
    ),
    fileName = cms.untracked.string('gem_EDM-qc8spec.root')
)
process.out = cms.EndPath(process.output)# + process.dqmEnv + process.dqmSaver)
