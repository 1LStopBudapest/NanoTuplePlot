import os, sys
import types

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_2016 import samples as samples_2016

samplesRun = ['UL17V9_Full99mm', 'TTToSemiLeptonic', 'TTTo2L2Nu']
fileperjobMC = 1
fileperjobData = 1
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
    tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
    fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
    for i in range(0, tfiles, fileperjobMC):
        txtline.append("python IVFHistMaker.py --sample %s --startfile %i --nfiles %i\n"%(sL, i, fileperjobMC))

fout = open("parallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir, "1DFiles/IVF")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []
bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)

for sL in samplesRun:
    bashline.append('hadd 1DHist_%s.root 1DHist_%s_*.root\n'%(sL, sL))
    bashline.append('mv 1DHist_%s.root %s\n'%(sL, Rootfilesdirpath))

l = str(" ".join(s for s in samplesRun))
bashline.append('python IVFPlot.py -l %s'%l)

fsh = open("parallelStackHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelStackHist.sh')
os.system('./parallelStackHist.sh')
os.system('rm *.root parallelJobsubmit.txt parallelStackHist.sh')
