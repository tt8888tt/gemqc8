# gemqc8
```bash
scram p -n QC8Test CMSSW CMSSW_10_5_0_pre2
cd QC8Test/src
cmsenv
git-cms-merge-topic jshlee:gem-vfatv3
scram b -j 4
git clone git@github.com:giovanni-mocellin/gemqc8.git
mv gemqc8/* .
rm -rf gemqc8
scram b -j 4
cd Analysis/GEMQC8/test
python launcher_validation.py 71 xslxTOcsv=OFF
```
