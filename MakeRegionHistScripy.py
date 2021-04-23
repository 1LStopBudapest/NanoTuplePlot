import os, sys

sys.path.append('../')
from Sample.SampleList import *
from Sample.Dir import plotDir
from Sample.FileList_2016 import samples as samples_2016


def get_parser():
    ''' Argument parser.                                                                                                                                                    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',             action='store',                    type=str,            default='Other'                                      help="run over which sample?" )
    argParser.add_argument('--region',             action='store',                    type=str,            default='SR',                                             help="Which region?" )
    return argParser

options = get_parser().parse_args()
    
reg = options.region
sample = options.sample

SigScan =  True if 'Signal' in sample else False
year = 2016
fileperjobMC = 1
fileperjobData = 1
TotJobs = 4

if year==2016:
    samplelist = samples_2016
elif year==2017:
    samplelist = samples_2017
else:
    samplelist = samples_2018

Rootfilesdirpath = os.path.join(plotDir,"RegionHistFiles")
if not os.path.exists(Rootfilesdirpath):
        os.makedirs(Rootfilesdirpath)

bashline = []

if SigScan:
    print 'Running over all the signal points'
    txtline = []
    for sig in signals:
        sname = 'T2tt_'+sig
        txtline.append("python RegionPlot.py --sample %s --region %s\n"%(sname, reg))
    fout = open("parallelJobsubmit.txt", "w")
    fout.write(''.join(txtline))
    fout.close()


    bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)
    bashline.append('mv RegionPlot_%s_*.root %s\n'%(reg, Rootfilesdirpath))

else:
    print 'Running over all the bkgs as well ass data (MET)'
    samplesRun = list(snameMap[k] for k in bkgs + data)
    print samplesRun


    
fsh = open("parallelRegionHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelRegionHist.sh')
#os.system('./parallelRegionHist.sh')
#os.system('rm *.root parallelJobsubmit.txt parallelRegionHist.sh')
