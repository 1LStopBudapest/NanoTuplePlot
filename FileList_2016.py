import os, sys

from Dir import userpath

MC_dir = ""
Data_dir = ""
Signal_dir = "StopSignal/"

samples = {}
#need to add more options like Xsec, Nevents etc.
samples['Stop_500_480_fast'] = [os.path.join(userpath, Signal_dir, "Stop_500_480/tau100mm/FastSim/"), 1.00]
samples['Stop_500_480_full'] = [os.path.join(userpath, Signal_dir, "Stop_500_480/tau100mm/FullSim/"), 1.00] 
