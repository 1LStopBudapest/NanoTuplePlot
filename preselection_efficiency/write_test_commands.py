import json


input_json_file = "/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/json_sample_info/summed_2018_reworked.json"
####################################################
#Read json with a dictionary including nevents per masspoints and BR
with open(input_json_file, "r") as f:
    masspoint_dict = json.load(f)

masspoint_list = []
threshold_mass = 50
total_masspoints = 0

for key, value in masspoint_dict.items():
    if isinstance(value, list):
        total_masspoints +=1
        mstop_, mx0_ = key.split('_')
        mstop_ = int(mstop_)
        mx0_ = int(mx0_)

        delta_m_ = abs(mstop_-mx0_)

        large_differences = delta_m_>threshold_mass
        same_mass = mstop_== mx0_
        zero_entries = value[0] < 1 and value[1] < 1
        few_events = value[0] + value[1] < 20

        if large_differences or same_mass or zero_entries or few_events:
            print("key dropped = "+key)
        else:
            masspoint_list.append(key)

print(masspoint_list)
print(len(masspoint_list))
print(total_masspoints)

tmp_condor = open('execute_test.sh', 'w')

for masspoint in masspoint_list:
    #tmp_condor.write('echo "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" \n')
    #tmp_condor.write('echo python 1DPlot_LL_BR_weighted_bothBR_genTest.py --sample Sig_Splitted_'+masspoint+' --startfile 0 --nfiles 10 --nevents 100000 --br 1.0 --year 2018 \n' )
    #tmp_condor.write('echo "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" \n')
    for br in ["0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9","1.0"]:
        tmp_condor.write('python 1DPlot_LL_BR_weighted_bothBR_newComb_peselection.py --sample Sig_Splitted_'+masspoint+' --startfile 0 --nfiles 10 --nevents 1000000 --br '+br+' --year 2018 \n' )
    #tmp_condor.write('\n')

tmp_condor.close()