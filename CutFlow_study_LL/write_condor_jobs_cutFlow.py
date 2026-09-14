import os

delta_m_stop = 25
delta_m_x0 = [10,15,20,25,30]
masspoint_list = []

for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        masspoint_list.append(str(mStop)+"_"+str(mX0))

year = '2018'

tmp_condor = open('jobs_2018/submitFile_stop_cutFlow.condor', 'w')
tmp_condor.write('''Executable = execute_condor_job_cutFlow.sh
Log        = jobs_2018/log_running_$(ProcId).log
Output     = jobs_2018/log_running_$(ProcId).out
Error      = jobs_2018/log_running_$(ProcId).error
Transfer_Input_Files = 1DPlot_LL_BR_weighted_bothBR_newComb_cutFlow.py
arguments  = $(info)
+JobFlavour = "longlunch" \n\n'''.format(here=os.environ['PWD']))
tmp_condor.write('queue info from ( \n')

for masspoint in masspoint_list:
    for br in ["0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9","1.0"]:
        tmp_condor.write('1DPlot_LL_BR_weighted_bothBR_newComb_cutFlow.py --sample Sig_Splitted_'+masspoint+' --startfile 0 --nfiles 10 --nevents 1000000 --br '+br+' --year '+year+' \n' )

tmp_condor.write(') \n')
tmp_condor.close()

print('condor_submit jobs_2018/submitFile_stop_cutFlow.condor')
