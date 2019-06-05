# gemqc8
```bash
scram p -n QC8Test CMSSW CMSSW_10_6_0_pre4
cd QC8Test/src
cmsenv
git clone git@github.com:giovanni-mocellin/gemqc8.git
mv gemqc8/* .
rm -rf gemqc8
scram b -j 4
cd Analysis/GEMQC8/test
python launcher_fast_efficiency.py 127 xlsxTOcsv=OFF
python launcher_validation.py 127 xlsxTOcsv=OFF ask_to_QC8_PFA_coordination
```
