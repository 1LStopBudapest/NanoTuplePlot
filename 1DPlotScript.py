import os, sys
import types
import ROOT

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_UL2016 import samples as samples_2016
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018
from Helper.PlotHelper import *

#samplesRun = ['WJetsToLNu', 'TTSingleLep_pow', 'MET_Data',]
samplesRun = ['TTV', 'VV', 'QCD', 'ZJetsToNuNu', 'ST', 'TTbar', 'WJetsToLNu', 'Sig_Prompt_500_420_full', 'Sig_Prompt_500_450_full', 'Sig_Prompt_500_470_full']
fileperjobMC = 4
fileperjobData = fileperjobMC
TotJobs = 4
year = '2016PostVFP'
nevts = -1

txtline = []

if year=='2016':
    samplelist = samples_2016
elif year=='2016PreVFP':
    samplelist = samples_2016Pre
elif year=='2016PostVFP':
    samplelist = samples_2016Post
elif year=='2017':
    samplelist = samples_2017
else:
    samplelist = samples_2018
            
    
for sL in samplesRun:
    if isinstance(samplelist[sL][0], types.ListType):
        for s in samplelist[sL]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
            tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
            for i in range(0, tfiles, fileperjob):
                txtline.append("python 1DPlot.py --sample %s --year %s --startfile %i --nfiles %i --nevents %d\n"%(sample, year, i, fileperjob, nevts))
    else:
        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjob):
            txtline.append("python 1DPlot.py --sample %s --year %s --startfile %i --nfiles %i --nevents %d\n"%(sL, year, i, fileperjob, nevts))
                
fout = open("parallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"1DHistFiles")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)

for sL in samplesRun:
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd 1DHist_%s.root 1DHist_%s*.root\n'%(sL, sLi))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd 1DHist_'+sL+'.root'+str("".join(' 1DHist_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd 1DHist_%s.root 1DHist_%s_*.root\n'%(sL, sL))
    bashline.append('mv 1DHist_%s.root %s\n'%(sL, Rootfilesdirpath))

    
fsh = open("parallel1DHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallel1DHist.sh')
#os.system('./parallel1DHist.sh')
os.system('rm *.root parallelJobsubmit.txt parallel1DHist.sh')


#Plotting section
doplots = True
vList = ['LeppT'] #should be same as in 1DPlot.py
files = []
for sl in samplesRun:
    if os.path.exists(Rootfilesdirpath+'/1DHist_'+sl+'.root'):
        files.append(ROOT.TFile.Open(Rootfilesdirpath+'/1DHist_'+sl+'.root'))
    else:
        doplots = False
        print 'Root files for',sl,'sample soes not exist. Please add , sl, to samplesRun list to run python 1DPlot.py --sample',sl

if doplots :
    for v in vList:
        #1D plot
        #for sl in samplesRun:
            #Plot1DExt(v, sl, '1DHist_'+sl+'.root', Rootfilesdirpath, islogy=True)
        #stackplot
        StackHistsNoDataExt(files, samplesRun, v, Rootfilesdirpath, 'Preselection')
        #comparison plot
       # CompareHistExt(files, samplesRun, v, 'Shape', Rootfilesdirpath)
        

