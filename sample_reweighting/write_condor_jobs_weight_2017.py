import os

#2017 post processed nanoaod
input_folder="/eos/cms/store/group/comm_luminosity/mleoncoe/test"
input_folder_=input_folder.replace("root://eosuser.cern.ch/","")

output_folder = "/eos/cms/store/group/comm_luminosity/mleoncoe/test2"

#runOn=[input_folder+f for f in os.listdir(input_folder) if not "BR_0.3" in f]
runOn=[input_folder+f for f in os.listdir(input_folder)]

print(runOn)

tmp_condor = open('jobs_2017/submitFile_stop_weight.condor', 'w')
tmp_condor.write('''Executable = execute_stop_weight.sh
Log        = jobs_2017/log_running_$(ProcId).log
Output     = jobs_2017/log_running_$(ProcId).out
Error      = jobs_2017/log_running_$(ProcId).error
Transfer_Input_Files = reweightingBRandctau_new.py
arguments  = $(info)
+JobFlavour = "longlunch" \n\n'''.format(here=os.environ['PWD']))
tmp_condor.write('queue info from ( \n')

for ifile in runOn:    
    tmp_condor.write('reweightingBRandctau_new.py {input} {output} \n'.format(input=ifile,output=output_folder  ) )

tmp_condor.write(') \n')
tmp_condor.close()

print('condor_submit jobs_2017/submitFile_stop_weight.condor')