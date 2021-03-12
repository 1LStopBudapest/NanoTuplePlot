import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_2016 import samples as samples_2016

samplesRun = ['TTV', 'QCD', 'DYJetsToLL', 'ZJetsToNuNu', 'VV', 'ST', 'TTSingleLep_pow', 'TTLep_pow', 'WJetsToLNu', 'MET_Data', 'T2tt_500_420', 'T2tt_500_490']
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
    if 'T2tt' in sL:
        txtline.append("python StackHistMaker.py --sample %s --startfile %i --nfiles %i\n"%(sL, 1, fileperjobMC))
    else:
        if isinstance(samplelist[sL][0], types.ListType):
            for s in samplelist[sL]:
                sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
                fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
                tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
                for i in range(0, tfiles, fileperjobMC):
                    txtline.append("python StackHistMaker.py --sample %s --startfile %i --nfiles %i\n"%(sample, i, fileperjobMC))
        else:
            tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
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
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd StackHist_%s.root StackHist_%s*.root\n'%(sL, sLi))
    elif 'T2tt' in sL:
        bashline.append('hadd StackHist_%s.root StackHist_%s*.root\n'%(sL, sL))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd StackHist_'+sL+'.root'+str("".join(' StackHist_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
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
