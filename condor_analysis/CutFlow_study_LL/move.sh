#!/bin/bash
python write_condor_jobs_cutFlow.py

mkdir -p temp1/analysis_output
mkdir -p temp1/analysis_output/csv
mkdir -p temp1/NanoTuplePlot
mkdir -p temp1/AuxFiles
mkdir -p temp1/ElectronRecoStudy
mkdir -p temp1/Helper
mkdir -p temp1/Sample
mkdir -p temp1/Plots

### CHANGE: pipeline folder to run ###
cp -r ../../CutFlow_study_LL ./temp1/NanoTuplePlot

cp -r ../../set_python_lxplus ./temp1/NanoTuplePlot
cp -r ../../VarHandler.py ./temp1/NanoTuplePlot
cp -r ../../../AuxFiles/* ./temp1/AuxFiles
cp -r ../../../ElectronRecoStudy/* ./temp1/ElectronRecoStudy
cp -r ../../../Helper/* ./temp1/Helper
cp -r ../../../Sample/* ./temp1/Sample


mkdir -p stop_analysis/output/
mkdir -p stop_analysis/error/
mkdir -p stop_analysis/log/

tar cf stop_analysis/payload.tar ./temp1
rm -r temp1

cp submitFile_stop_cutFlow.condor ./stop_analysis/
cp write_condor_jobs_cutFlow.py ./stop_analysis/

chmod +x execute_condor_job.sh
cp execute_condor_job.sh ./stop_analysis/

### CHANGE: your EOS workspace ###
# on lxplus: module load lxbatch/eossubmit
scp -r ./stop_analysis/* mleoncoe@lxplus.cern.ch:/eos/user/m/mleoncoe/analysis_stop/condorRuns/test1

rm -r stop_analysis
