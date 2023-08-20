import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016 import samples as samples_2016

samplesRun = ['WJetsToLNu', 'TTbar']
fileperjobMC = 1 
fileperjobData = 1
TotJobs = 4
year = '2016PostVFP'

txtline = []

if year=='2016PreVFP':
    samplelist = samples_2016Pre
elif year=='2016PostVFP':
    samplelist = samples_2016Post
elif year=='2016':
    samplelist = samples_2016
elif year=='2017':
    samplelist = samples_2017
else:
    samplelist = samples_2018

sigFileList = []

for sL in samplesRun:
    if 'T2tt_prompt' in sL:
        sigFileList = os.listdir(samplelist['T2tt_prompt'][0])
        sigFileList = [s[:-len('.root')] for s in sigFileList]
        for i in range(0, len(sigFileList), fileperjobMC):
            txtline.append("python RegionPlot.py --sample %s --startfile %i --nfiles %i --year %s\n"%(sigFileList[i], 0, fileperjobMC, year))
    elif isinstance(samplelist[sL][0], types.ListType):
        for s in samplelist[sL]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
            tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
            for i in range(0, tfiles, fileperjobMC):
                txtline.append("python RegionPlot.py --sample %s --startfile %i --nfiles %i --year %s\n"%(sample, i, fileperjobMC, year))
    else:
        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjobMC):
            txtline.append("python RegionPlot.py --sample %s --startfile %i --nfiles %i --year %s\n"%(sL, i, fileperjobMC, year))
                
fout = open("parallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"RegionFiles/extension")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)

for sL in samplesRun:
    if 'T2tt_prompt' in sL:
        for sFL in sigFileList:
            bashline.append('hadd RegionPlot_SR_%s.root RegionPlot_SR_%s_*.root\n'%(sFL, sFL))
            bashline.append('mv RegionPlot_SR_%s.root %s\n'%(sFL, Rootfilesdirpath))
    else:
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd RegionPlot_SR_%s.root RegionPlot_SR_%s*.root\n'%(sL, sLi))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd RegionPlot_SR_'+sL+'.root'+str("".join(' RegionPlot_SR_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd RegionPlot_SR_%s.root RegionPlot_SR_%s_*.root\n'%(sL, sL))
    bashline.append('mv RegionPlot_SR_%s.root %s\n'%(sL, Rootfilesdirpath))

l = str(" ".join(s for s in samplesRun)) #l = str(" ".join(s for s in sigFileList))
bashline.append('python StackPlot_Region.py -l %s'%l)
    
fsh = open("parallelStackHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelStackHist.sh')
os.system('./parallelStackHist.sh')
os.system('rm *.root parallelJobsubmit.txt parallelStackHist.sh')
