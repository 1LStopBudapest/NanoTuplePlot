import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_UL2016 import samples as samples_2016
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018


samplesRun = ['WJetsToLNu', 'TTbar', 'ST', 'DYJetsToLL', 'ZJetsToNuNu', 'QCD', 'TTV', 'VV', 'Sig_Displaced_300_290_full', 'Sig_Displaced_350_335_full', 'Sig_Displaced_400_380_full']
#samplesRun = ['TTbar', 'QCD', 'Sig_Displaced_350_335_full']


#fileperjobMC = 2 
fileperjobMC = 1 
fileperjobData = 1
TotJobs = 1
year = '2018'

txtline = []

#Moises
nsamples = 5
nevents = 1000000
processed_samples = 0
processed_samples_i = 0
processed_samples_j = 0

#######

if year=='2016PreVFP':
    samplelist = samples_2016Pre
    DataLumi = SampleChain.luminosity_2016PreVFP
elif year=='2016PostVFP':
    samplelist = samples_2016Post
    DataLumi = SampleChain.luminosity_2016PostVFP
elif year=='2016':
    samplelist = samples_2016
    DataLumi = SampleChain.luminosity_2016
elif year=='2017':
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018
    DataLumi = SampleChain.luminosity_2018

for sL in samplesRun:
    if isinstance(samplelist[sL][0], types.ListType):
        #Moises Debug
        print("....................")
        print("sL = "+str(sL))
        print("samplelist[sL][0] = "+str(samplelist[sL][0]))
        print("....................")
        #####

        for s in samplelist[sL]:

            
            #Moises
            processed_samples = processed_samples+1
            if processed_samples > nsamples:
                print("continuee")
                continue

            print("********************")
            print("s = "+str(s))
            print("samplelist[sL] = "+str(samplelist[sL]))
            
            print("*******************")
            ########

            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            #Moises
            #print("len(SampleChain.getfilelist(samplelist[sample][0])) = "+str(len(SampleChain.getfilelist(samplelist[sample][0]))))
            #print("SampleChain.getfilelist(samplelist[sample][0]) = "+str(SampleChain.getfilelist(samplelist[sample][0])))
            ####

            fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
            tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
            for i in range(0, tfiles, fileperjobMC):
                #txtline.append("python StackHistMaker_LL_std.py --sample %s --startfile %i --nfiles %i\n"%(sample, i, fileperjobMC))
                #Moises
                processed_samples_i = processed_samples_i+1
                if processed_samples_i > nsamples: continue
                txtline.append("python StackHistMaker_LL_std.py --sample %s --nevents %i --startfile %i --nfiles %i\n"%(sample, nevents, i, fileperjobMC))
                ###
            #Moises
            processed_samples_i = 0
    else:
        #Moises
        
        processed_samples = processed_samples+1
        if processed_samples > nsamples: 
            print("continuee")
            continue

        print("....NOT A LIST.......")
        print("sL = "+str(sL))
        print("samplelist[sL][0] = "+str(samplelist[sL][0]))
        print("....................")
        ########

        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjobMC):
            #txtline.append("python StackHistMaker_LL_std.py --sample %s --startfile %i --nfiles %i\n"%(sL, i, fileperjobMC))
            #Moises
            if processed_samples > nsamples: continue
            txtline.append("python StackHistMaker_LL_std.py --sample %s --nevents %i --startfile %i --nfiles %i\n"%(sL, nevents, i, fileperjobMC))
            ###
    #Moises
    processed_samples = 0
    #######
                
fout = open("parallelJobsubmit_std.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"StackFiles/Displaced/Dxy2")
#Moises
Rootfilesdirpath_added = os.path.join(plotDir,"StackFiles/Displaced/Dxy2/total")
#####
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)
    #Moises
    os.makedirs(Rootfilesdirpath_added)
    #####

bashline = []    
bashline.append('parallel --jobs %i < parallelJobsubmit_std.txt\n'%TotJobs)

for sL in samplesRun:

    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd StackHist_%s_std.root StackHist_%s*_std.root\n'%(sL, sLi))

    elif isinstance(samplelist[sL][0], types.ListType):

        #sLi = 'hadd StackHist_'+sL+'.root'+str("".join(' StackHist_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        #Moises
        sLi = 'hadd StackHist_' + sL + '_std.root'
        file_patterns = []
        for s in samplelist[sL]:
            #Moises
            processed_samples_j = processed_samples_j+1
            if processed_samples_j > nsamples:
                print("continuee")
                continue
            ####
            # Find the corresponding key for the current sample value
            sample_key = list(samplelist.keys())[list(samplelist.values()).index(s)]
            file_pattern = ' StackHist_' + sample_key + '*_std.root'
            file_patterns.append(file_pattern)
        # Join the file patterns into a single string and append to the base string
        sLi += str("".join(file_patterns))
        processed_samples_j = 0
        #####

        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd StackHist_%s_std.root StackHist_%s_*_std.root\n'%(sL, sL))

    #bashline.append('mv StackHist_%s.root %s\n'%(sL, Rootfilesdirpath))
    #Moises
    bashline.append('mv StackHist_%s_std.root %s\n'%(sL, Rootfilesdirpath_added))
    #####

bashline.append('mv StackHist_*_std.root %s\n'%(Rootfilesdirpath))

l = str(" ".join(s for s in samplesRun))
bashline.append('python  StackPlot_LL_std.py -l %s'%l)
    
fsh = open("parallelStackHist_std.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelStackHist_std.sh')
os.system('./parallelStackHist_std.sh')
#os.system('rm *.root parallelJobsubmit.txt parallelStackHist_std.sh')

