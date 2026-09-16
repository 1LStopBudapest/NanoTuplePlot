#!/bin/bash

# remember to +x this!
echo $(hostname)
WAIT=true

if [[ $(hostname) == *"higgs.elte.hu" ]]; then
   echo "incorrect host"
fi



if [[ $(hostname) == *"higgs.elte.hu" ]]; then
   echo "Incorrect host"
else
   tar xf payload.tar -C ./
   mv temp1/* ./
   ### CHANGE: pipeline folder ###
   rm -f NanoTuplePlot/CutFlow_study_LL/info_test_*.csv

   echo 'i am in this directory'
   echo $PWD

   source NanoTuplePlot/set_python_lxplus/set_env.sh

   ### CHANGE: pipeline folder ###
   cd NanoTuplePlot/CutFlow_study_LL

   echo 'i am in this directory'
   echo $PWD

   # echo 'contents of this directory'
   # echo $LS
   # ls

   ### CHANGE: add slots if your driver takes more flags ###
   echo " will run this source ${1} ${2} ${3} ${4} ${5} ${6} ${7} ${8} ${9} ${10} ${11} ${12} ${13}"

   python ${1} ${2} ${3} ${4} ${5} ${6} ${7} ${8} ${9} ${10} ${11} ${12} ${13}

   echo 'copying output files'
   cd ..
   cd ..
   cp -r Plots analysis_output
   ### CHANGE: pipeline folder ###
   for f in NanoTuplePlot/CutFlow_study_LL/*.csv; do
      [ -e "$f" ] || continue
      b=$(basename "$f" .csv)
      ### CHANGE: ${3}=sample, ${11}=BR, counted in the command above ###
      cp "$f" "analysis_output/csv/${b}_${3}_BR_${11}_${PROCID}.csv"
   done

   echo 'done'
fi
