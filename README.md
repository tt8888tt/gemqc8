# gemqc8
```
cmsrel CMSSW_10_6_0_pre3
cd CMSSW_10_6_0_pre3/src
cmsenv
git cms-merge-topic jshlee:gem-vfatv3
git cms-merge-topic hyunyong:10_5_0_pre2_QC8_Geo
git clone git@github.com:gem-sw/gemqc8.git
scram b -j12
cd gemqc8/Analysis/test
cmsRun runGEMCosmicStand_sim.py
```
