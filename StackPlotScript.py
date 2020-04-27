import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir

samplesRun = ['WJetsToLNu', 'TTSingleLep_pow', 'MET_Data',]
fileperjobMC = 1 
fileperjobData = 1
TotJobs = 4

txtline = []

for sL in samplesRun:
    if isinstance(SampleChain.samplelist[sL][0], types.ListType):
        for s in SampleChain.samplelist[sL]:
            sample = list(SampleChain.samplelist.keys())[list(SampleChain.samplelist.values()).index(s)]
            fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
            tfiles = len(SampleChain.getfilelist(SampleChain.samplelist[sample][0]))
            for i in range(0, tfiles, fileperjobMC):
                txtline.append("python StackHistMaker.py --sample %s --startfile %i --nfiles %i\n"%(sample, i, fileperjobMC))
    else:
        tfiles = len(SampleChain.getfilelist(SampleChain.samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjobMC):
            txtline.append("python StackHistMaker.py --sample %s --startfile %i --nfiles %i\n"%(sL, i, fileperjobMC))
                
fout = open("parallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"StackFiles")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)

for sL in samplesRun:
    bashline.append('hadd StackHist_%s.root StackHist_%s_*.root\n'%(sL, sL))
    bashline.append('mv StackHist_%s.root %s\n'%(sL, Rootfilesdirpath))

l = str(" ".join(s for s in samplesRun))
bashline.append('python  StackPlot.py -l %s'%l)
    
fsh = open("parallelStackHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelStackHist.sh')
os.system('./parallelStackHist.sh')
os.system('rm *.root parallelJobsubmit.txt parallelStackHist.sh')
