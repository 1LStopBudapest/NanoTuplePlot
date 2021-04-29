import os, sys
import types

sys.path.append('../')
from Sample.SampleList import *
from Sample.Dir import plotDir
from Sample.FileList_2016 import samples as samples_2016
from Sample.SampleChain import SampleChain

def get_parser():
    ''' Argument parser.                                                                                                                                                    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',             action='store',                    type=str,            default='Other',                                      help="run over which sample?" )
    argParser.add_argument('--region',             action='store',                    type=str,            default='SR',                                             help="Which region?" )
    return argParser

options = get_parser().parse_args()
    
reg = options.region
sample = options.sample

SigScan =  True if 'Signal' in sample else False
year = 2016
fileperjobMC = 2
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
    print 'Running over all the bkgs as well as data (MET)'
    samplesRun = list(snameMap[k] for k in bkgs + data)
    print samplesRun
    txtline = []
    for sL in samplesRun:
        if isinstance(samplelist[sL][0], types.ListType):
            for s in samplelist[sL]:
                sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
                fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
                tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
                for i in range(0, tfiles, fileperjob):
                    txtline.append("python RegionPlot.py --sample %s --startfile %i --nfiles %i --region %s\n"%(sample, i, fileperjob, reg))
        else:
            tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
            fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
            for i in range(0, tfiles, fileperjob):
                txtline.append("python RegionPlot.py --sample %s --startfile %i --nfiles %i --region %s\n"%(sL, i, fileperjob, reg))
    fout = open("parallelJobsubmit.txt", "w")
    fout.write(''.join(txtline))
    fout.close()

    bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)
    for sL in samplesRun:
        if 'Data' in sL:
            sLi = sL.replace('Data','')+'Run'
            bashline.append('hadd RegionPlot_%s_%s.root RegionPlot_SR_%s*.root\n'%(reg, sL, sLi))
        elif isinstance(samplelist[sL][0], types.ListType):
            sLi = 'hadd RegionPlot_'+reg+'_'+sL+'.root'+str("".join(' RegionPlot_'+reg+'_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
            bashline.append('%s\n'%sLi)
        else:
            bashline.append('hadd RegionPlot_%s_%s.root RegionPlot_%s_%s_*.root\n'%(reg, sL, reg, sL))
        bashline.append('mv RegionPlot_%s_%s.root %s\n'%(reg, sL, Rootfilesdirpath))
                
fsh = open("parallelRegionHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelRegionHist.sh')
os.system('./parallelRegionHist.sh')
os.system('rm *.root parallelJobsubmit.txt parallelRegionHist.sh')
