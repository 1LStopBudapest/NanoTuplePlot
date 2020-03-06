import os, sys

from Dir import userpath

MC_dir = "PostProcessedNtuple/2016/MetSingleLep/"
Data_dir = MC_dir
Signal_dir = "StopSignal/"

samples = {}
#need to add more options like Xsec, Nevents etc.
samples['Stop_500_480_fast'] = [os.path.join(userpath, Signal_dir, "Stop_500_480/tau100mm/FastSim/"), 1.00]
samples['Stop_500_480_full'] = [os.path.join(userpath, Signal_dir, "Stop_500_480/tau100mm/FullSim/"), 1.00] 

samples['TTSingleLep_pow'] = [os.path.join(userpath, MC_dir, "TTSingleLep_pow/"), 1.00]
