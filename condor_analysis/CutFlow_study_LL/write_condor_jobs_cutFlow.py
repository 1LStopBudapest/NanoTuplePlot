import os

### CHANGE: mass point grid ###
delta_m_stop = 25
delta_m_x0 = [10,15,20,25,30]
masspoint_list = []

for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        masspoint_list.append(str(mStop)+"_"+str(mX0))

### CHANGE: year ###
year = '2018'

### CHANGE: job time limit below (espresso=20min, longlunch=2h, workday=8h) ###
tmp_condor = open('submitFile_stop_cutFlow.condor', 'w')
tmp_condor.write('''Executable = execute_condor_job.sh
Log        = log/log_running_$(ProcId).log
Output     = output/log_running_$(ProcId).out
Error      = error/log_running_$(ProcId).error
Transfer_Input_Files = payload.tar
transfer_output_files   = analysis_output
arguments  = $(info)
environment = "PROCID=$(ProcId)"
MY.WantOS = "el7"
MY.SendCredential = True
+JobFlavour = "espresso" \n\n'''.format(here=os.environ['PWD']))
tmp_condor.write('queue info from ( \n')

njobs = 0

for masspoint in masspoint_list:
    for br in ["0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9","1.0"]:

        ### CHANGE: max jobs, lower it for a test run ###
        if njobs>10000:
            continue
        njobs+=1

        ### CHANGE: driver script and its flags ###
        tmp_condor.write('1DPlot_test_lepton_truth_TM_comparison.py --sample Sig_Splitted_'+masspoint+' --startfile 0 --nfiles 10 --nevents 1000000 --br '+br+' --year '+year+' \n' )

tmp_condor.write(') \n')
tmp_condor.close()

#print('condor_submit submitFile_stop_cutFlow.condor')
print('done, now move to condor')
