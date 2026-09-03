import os, sys
import types

sys.path.append('../')
from Sample.SampleList import *
from Sample.Dir import plotDir
from Sample.FileList_LLStops2016PreVFP import samples as samples_2016Pre
from Sample.FileList_LLStops2016PostVFP import samples as samples_2016Post
from Sample.FileList_LLStops2017 import samples as samples_2017
from Sample.FileList_LLStops2018 import samples as samples_2018
from Sample.LLStopsSampleChain import SampleChain


def get_parser():
    ''' Argument parser.                                                                                                                                                    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',             action='store',                    type=str,            default='Signal',                                      help="run over which sample, Signal or Other?" )
    argParser.add_argument('--region',             action='store',                    type=str,            default='SR+CR',                                             help="Which region?" )
    argParser.add_argument('--dc',             action='store',                    type=str,            default='count',                                             help="What type of datacard?" )
    return argParser

options = get_parser().parse_args()
    
reg = options.region
sample = options.sample
dc = options.dc

SigScan =  True if 'Signal' in sample else False
script = 'LLSigCountDCHist' if dc=='count' else 'LLSigShapeDCHist'
year = '2018'
nevts = -1
fileperjobMC = 4
TotJobs = 4

if year=='2016PreVFP':
    samplelist = samples_2016Pre
elif year=='2016PostVFP':
    samplelist = samples_2016Post
elif year=='2017':
    samplelist = samples_2017
else:
    samplelist = samples_2018

Rootfilesdirpath = os.path.join(plotDir,"LLSigDCFiles")
if not os.path.exists(Rootfilesdirpath):
        os.makedirs(Rootfilesdirpath)

BrFrac = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']

bashline = []

if SigScan:
    print 'Running over all the signal points'
    txtline = []
    for sig in LLsignals[year]:
        sname = 'stopLL_'+sig
        for br in BrFrac:
            txtline.append("python %s.py --sample %s --BR %s --region %s --year %s --nevents %d\n"%(script, sname, br, reg, year, nevts))
    fout = open("parallelJobsubmit.txt", "w")
    fout.write(''.join(txtline))
    fout.close()


    bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)
    for sig in LLsignals[year]:
        sname = 'stopLL_'+sig
        for br in BrFrac:
            bashline.append('mv %s_%s_%s_%s*.root %s_%s_%s_%s.root\n'%(script, reg, sname, br, script, reg, sname, br))
    bashline.append('mv %s_%s*.root %s\n'%(script, reg, Rootfilesdirpath))

else:
    print 'This script is for LL signal grid only, please run with --sample Signal option'
                
fsh = open("LLSigDCHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 LLSigDCHist.sh')
os.system('./LLSigDCHist.sh')
#os.system('rm *.root parallelJobsubmit.txt LLSigDCHist.sh')
