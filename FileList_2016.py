import os, sys

from Dir import userpath

MC_dir = "PostProcessedNtuple/2016/MetSingleLep/"
Data_dir = MC_dir
Signal_dir = "StopSignal/"

samples = {}
#need to add more options like Xsec, Nevents etc.
samples['Stop_500_480_fast'] = [os.path.join(userpath, Signal_dir, "Stop_500_480/tau10mm/FastSim/"), 1.00]
samples['Stop_500_480_full'] = [os.path.join(userpath, Signal_dir, "Stop_500_480/tau10mm/FullSim/"), 1.00] 

samples['TTSingleLep_pow'] = [os.path.join(userpath, MC_dir, "TTSingleLep_pow/"), 1.00]
samples['TTLep_pow'] = [os.path.join(userpath, MC_dir, "TTLep_pow/"), 1.00]
samples['WJetsToLNu_HT70to100'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT70to100/"), 1.00]
samples['WJetsToLNu_HT100to200'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT100to200/"), 1.00]
samples['WJetsToLNu_HT200to400'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT200to400/"), 1.00]
samples['WJetsToLNu_HT400to600'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT400to600/"), 1.00]
samples['WJetsToLNu_HT600to800'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT600to800/"), 1.00]
samples['WJetsToLNu_HT800to1200'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT800to1200/"), 1.00]
samples['WJetsToLNu_HT1200to2500'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT1200to2500/"), 1.00]
samples['WJetsToLNu_HT2500toInf'] = [os.path.join(userpath, MC_dir, "WJetsToLNu_HT2500toInf/"), 1.00]

