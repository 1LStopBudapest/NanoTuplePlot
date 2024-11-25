import os, sys
import types

sys.path.append('../')
from Sample.SampleList import *
from Sample.Dir import plotDir
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018
from Sample.SampleChain import SampleChain

def get_parser():
    ''' Argument parser.                                                                                                                                                    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',             action='store',                    type=str,            default='Signal',                                      help="run over which sample, Signal or Other?" )
    argParser.add_argument('--region',             action='store',                    type=str,            default='SR',                                             help="Which region?" )
    argParser.add_argument('--dc',             action='store',                    type=str,            default='count',                                             help="What type of datacard?" )
    return argParser

options = get_parser().parse_args()
    
reg = options.region
sample = options.sample
dc = options.dc

SigScan =  True if 'Signal' in sample else False
script = 'CountDCHistJEC' if dc=='count' else 'ShapeDCHistJEC'
year = '2018'
nevts = 100000
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

Rootfilesdirpath = os.path.join(plotDir,"PromptDCFiles")
if not os.path.exists(Rootfilesdirpath):
        os.makedirs(Rootfilesdirpath)

bashline = []

if SigScan:
    print 'Running over all the signal points'
    txtline = []
    for sig in signals:
        sname = 'T2tt_'+sig
        txtline.append("python %s.py --sample %s --region %s --year %s --nevents %d\n"%(script, sname, reg, year, nevts))
    fout = open("parallelJobsubmit.txt", "w")
    fout.write(''.join(txtline))
    fout.close()


    bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)
    for sig in signals:
        sname = 'T2tt_'+sig
        bashline.append('mv %s_%s_%s*.root %s_%s_%s.root\n'%(script, reg, sname, script, reg, sname))
    bashline.append('mv %s_%s*.root %s\n'%(script, reg, Rootfilesdirpath))

else:
    print 'Running over all the bkgs'
    samplesRun = list(snameMap[k] for k in bkgs)
    print samplesRun
    txtline = []
    for sL in samplesRun:
        if isinstance(samplelist[sL][0], types.ListType):
            for s in samplelist[sL]:
                sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
                fileperjob = fileperjobMC
                tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
                for i in range(0, tfiles, fileperjob):
                    txtline.append("python %s.py --sample %s --startfile %i --nfiles %i --region %s --year %s --nevents %d\n"%(script, sample, i, fileperjob, reg, year,  nevts))
        else:
            tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
            fileperjob = fileperjobMC
            for i in range(0, tfiles, fileperjob):
                txtline.append("python %s.py --sample %s --startfile %i --nfiles %i --region %s --year %s --nevents %d\n"%(script, sL, i, fileperjob, reg, year, nevts))
    fout = open("parallelJobsubmit.txt", "w")
    fout.write(''.join(txtline))
    fout.close()

    bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)
    for sL in samplesRun:
        if isinstance(samplelist[sL][0], types.ListType):
            sLi = 'hadd '+script+'_'+reg+'_'+sL+'.root '+str("".join(script+'_'+reg+'_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root ' for s in samplelist[sL]))
            bashline.append('%s\n'%sLi)
        else:
            bashline.append('hadd %s_%s_%s.root %s_%s_%s_*.root\n'%(script, reg, sL, script, reg, sL))
        bashline.append('mv %s_%s_%s.root %s\n'%(script, reg, sL, Rootfilesdirpath))
                
fsh = open("PromptDCHistJEC.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 PromptDCHistJEC.sh')
os.system('./PromptDCHistJEC.sh')
#os.system('rm *.root parallelJobsubmit.txt PromptDCHistJEC.sh')
