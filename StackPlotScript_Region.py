import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

samplesRun = ['WJetsToLNu', 'TTbar', 'ST', 'DYJetsToLL', 'ZJetsToNuNu', 'QCD', 'TTV', 'VV']
fileperjobMC = 2 
fileperjobData = 1
TotJobs = 4
year = '2018'
reg = 'SR'

txtline = []

if year=='2016PreVFP':
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
                txtline.append("python RegionPlot.py --sample %s --startfile %i --nfiles %i --year %s --region %s\n"%(sample, i, fileperjob, year, reg))
    else:
        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjob
        for i in range(0, tfiles, fileperjob):
            txtline.append("python RegionPlot.py --sample %s --startfile %i --nfiles %i --year %s --region %s\n"%(sL, i, fileperjob, year, reg))
                
fout = open("parallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"RegionFiles")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)

for sL in samplesRun:
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd RegionPlot_%s_%s.root RegionPlot_%s_%s*.root\n'%(reg, sL, reg, sLi))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd RegionPlot_'+reg+'_'+sL+'.root'+str("".join(' RegionPlot_'+reg+'_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd RegionPlot_%s_%s.root RegionPlot_%s_%s_*.root\n'%(reg, sL, reg, sL))
    bashline.append('mv RegionPlot_%s_%s.root %s\n'%(reg, sL, Rootfilesdirpath))

#l = str(" ".join(s for s in samplesRun))
#bashline.append('python StackPlot_Region.py -l %s'%l)
    
fsh = open("parallelStackHistReg.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelStackHistReg.sh')
#os.system('./parallelStackHist.sh')
#os.system('rm *.root parallelJobsubmit.txt parallelStackHistReg.sh')
