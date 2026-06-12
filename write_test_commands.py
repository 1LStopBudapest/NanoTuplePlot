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
#print(masspoint_list[0])
masspoints_isolated = [u'375_360', u'300_285', u'300_280', u'475_450', u'475_455', u'350_340', u'325_305', u'325_300', u'250_240', u'900_870', u'250_230', u'700_670', u'350_335', u'450_425', u'450_420', u'275_265', u'275_260', u'750_720', u'500_480', u'500_485', u'300_270', u'300_275', u'500_490', u'300_290', u'425_405', u'425_400', u'475_445', u'375_365', u'325_310', u'325_315', u'250_225', u'250_220', u'275_250', u'275_255', u'425_410', u'350_320', u'350_325', u'425_415', u'800_770', u'475_460', u'375_350', u'375_355', u'400_385', u'400_380', u'1000_970', u'950_920', u'850_820', u'250_235', u'500_475', u'500_470', u'475_465', u'600_570', u'275_245', u'400_375', u'325_295', u'550_520', u'400_370', u'425_395', u'450_430', u'450_435', u'350_330', u'450_440', u'375_345', u'400_390', u'650_620']


tmp_condor = open('execute_test.sh', 'w')

for masspoint in masspoint_list:
    #tmp_condor.write('echo "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" \n')
    #tmp_condor.write('echo python 1DPlot_LL_BR_weighted_bothBR_genTest.py --sample Sig_Splitted_'+masspoint+' --startfile 0 --nfiles 10 --nevents 100000 --br 1.0 --year 2018 \n' )
    #tmp_condor.write('echo "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" \n')
    for br in ["0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9","1.0"]:
        tmp_condor.write('python 1DPlot_LL_BR_weighted_bothBR_newComb_test.py --sample Sig_Splitted_'+masspoint+' --startfile 0 --nfiles 10 --nevents 1000000 --br '+br+' --year 2018 \n' )
    #tmp_condor.write('\n')

tmp_condor.close()