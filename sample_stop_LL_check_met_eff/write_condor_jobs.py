import json,math
import os,sys,re

#input_folder="/media/moises/Data/workspacePcElte/sampleSplitting/susySamples/2017/privateNanoAodPriya/0000/"
#output_folder = "/media/moises/Data/workspacePcElte/sample_stop_LL_test_condor/outputs/"

#input_folder="/eos/cms/store/group/phys_susy/hephy/StopsCompressed/nanoTuples/compstops_UL16APVv9_nano_v6/Met/SMS_T2tt_mStop_250to1100_dM_10to30_LL/"
#2016 private nanoaod
#input_folder="/eos/cms/store/group/phys_susy/hephy/StopsCompressed/SMS-T2tt-4bd_genMET-100_genHT200_mStop-250To1100_dM-10To30_TuneCP5_LLStop_13TeV-madgraphMLM-pythia8/crab_RunIISummer20UL16MiniAODv2-FSUL16_106X_mcRun2_asymptotic_v17-v1_privateUL16nanov9/0000/"
#2017 private nanoaod
#input_folder="/eos/user/m/mleoncoe/stop_event_check/privateNanoAod2017/"
#2018 private nanoaod
input_folder="/eos/user/m/mleoncoe/stop_event_check/privateNanoAod2018/"

output_folder = "/afs/cern.ch/work/m/mleoncoe/private/stop_event_check/outputs_2018/"

runOn=[input_folder+f for f in os.listdir(input_folder)]
tmp_condor = open('jobs_2018/submitFile_stop_check.condor', 'w')
tmp_condor.write('''Executable = execute_stop_check.sh
getenv      = True
Log        = jobs_2018/log_running_$(ProcId).log
Output     = jobs_2018/log_running_$(ProcId).out
Error      = jobs_2018/log_running_$(ProcId).error
Transfer_Input_Files = stop_check_BR_branches_per_event_search.py
arguments  = $(info)
+JobFlavour = "tomorrow" \n\n'''.format(here=os.environ['PWD']))
tmp_condor.write('queue info from ( \n')

for ifile in runOn:
    file_name = os.path.basename(ifile)  # Gets "report.pdf"
    file_name_no_extension = os.path.splitext(file_name)[0]
    tmp_condor.write('stop_check_BR_branches_per_event_search.py {input} {output} \n'.format(input=ifile,output=output_folder+file_name_no_extension+".json"  ) )

tmp_condor.write(') \n')
tmp_condor.close()

print('condor_submit jobs_2018/submitFile_stop_check.condor')