# gemqc8
If you want to analyse QC8 real data:
```bash
scram p -n QC8Test CMSSW CMSSW_10_6_0
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

If you want to run simulations, download the package following these instructions:
```bash
scram p -n QC8Test CMSSW CMSSW_10_6_0
cd QC8Test/src
cmsenv
git clone git@github.com:giovanni-mocellin/gemqc8.git
mv gemqc8/* .
rm -rf gemqc8
rm -rf EventFilter
scram b -j 4
cd Analysis/GEMQC8/test
python launcher_sim_fast_efficiency.py 1 xlsxTOcsv=OFF
python launcher_sim.py 1 xlsxTOcsv=OFF
```
