import json,math
import os,sys,re

#2018 split LL stops
input_folder="/data/stopLongLived/displaced2018/T2tt_LL/"
output_folder = "/data/stopLongLived/displaced2018/T2tt_LL_processed"

runOn=[input_folder+f for f in os.listdir(input_folder)]

tmp_condor = open('run_weighting.sh', 'w')

for ifile in runOn:    
    tmp_condor.write('python reweightingBRandctau_new.py {input} {output} \n'.format(input=ifile,output=output_folder  ) )

tmp_condor.close()

print('source run_weighting.sh')