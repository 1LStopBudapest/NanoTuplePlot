import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_2016 import samples as samples_2016

#samplesRun = ['WJetsToLNu', 'TTSingleLep_pow', 'MET_Data',]
samplesRun = ['MET_Data',]
fileperjobMC = 2
fileperjobData = fileperjobMC
TotJobs = 4
year = 2016

txtline = []

if year==2016:
    samplelist = samples_2016
elif year==2017:
    samplelist = samples_2017
else:
    samplelist = samples_2018

for sL in samplesRun:
    if isinstance(samplelist[sL][0], types.ListType):
        for s in samplelist[sL]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
            tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
            for i in range(0, tfiles, fileperjobMC):
                txtline.append("python CutFlowHist.py --sample %s --startfile %i --nfiles %i\n"%(sample, i, fileperjobMC))
    else:
        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjobMC):
            txtline.append("python CutFlowHist.py --sample %s --startfile %i --nfiles %i\n"%(sL, i, fileperjobMC))
                
fout = open("parallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"CutFlowFiles")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)

for sL in samplesRun:
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd CFHist_%s.root CFHist_%s*.root\n'%(sL, sLi))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd CFHist_'+sL+'.root'+str("".join(' CFHist_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd CFHist_%s.root CFHist_%s_*.root\n'%(sL, sL))
    bashline.append('mv CFHist_%s.root %s\n'%(sL, Rootfilesdirpath))

    
fsh = open("parallelCFHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
#os.system('chmod 744 parallelStackHist.sh')
#os.system('./parallelStackHist.sh')
#os.system('rm *.root parallelJobsubmit.txt parallelStackHist.sh')
