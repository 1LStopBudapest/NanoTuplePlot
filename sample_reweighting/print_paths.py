import os
import json

# === User settings ===
folder_path = "/data/stopLongLived/displaced2018/T2tt_LL_processed" # Path to folder containing JSON files

# === Loop through files ===
for filename in os.listdir(folder_path):
    if filename.endswith(".root"):
        filepath = os.path.join(folder_path, filename)
        #print(filepath)
        filename_info = filename.replace("merged_stopLL_","")
        filename_info = filename_info.replace("_processed.root","")
        filename_info = filename_info.replace("BR_","")
        mstop_, mX0_, BR_ = filename_info.split("_")
        # print(mstop)
        # print(mX0)
        # print(BR_)
        mstop = float(mstop_)
        mX0 = float(mX0_)
        BR_float = float(BR_)
        delta_m = mstop-mX0
        key_ = "Sig_Splitted_"+mstop_+"_"+mX0_+"_"+BR_
        

        #samples['Sig_Splitted_250_240'] = [os.path.join(userpath, NoSplittedSignal_dir, '250_240_files/'), ]
        #print()
        print("samples['{}']= ['{}', ] ".format(key_, filepath))
