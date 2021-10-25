import os, sys
import ROOT
import types

from FillHistos_IVF import FillHistos_IVF

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_2016 import samples as samples_2016


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='UL17V9_Full99mm',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    

    return argParser

options = get_parser().parse_args()

samples  = options.sample
year = options.year

DataLumi=1.0

if year==2016:
    samplelist = samples_2016 
    DataLumi = SampleChain.luminosity_2016
elif year==2017:
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018
    DataLumi = SampleChain.luminosity_2018



histext = ''

Rootfilesdirpath = os.path.join(plotDir, "1DFiles/IVF")
if not os.path.exists(Rootfilesdirpath): 
    os.makedirs(Rootfilesdirpath)

histext = samples

if isinstance(samplelist[samples][0], types.ListType):
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['nSV'] = HistInfo(hname = 'nSV', sample = histext, binning=[20,0,20], histclass = ROOT.TH1F).make_hist()
        histos['Ntracks'] = HistInfo(hname = 'Ntracks', sample = histext, binning=[20,0,20], histclass = ROOT.TH1F).make_hist()
        histos['SVdxy'] = HistInfo(hname = 'SVdxy', sample = histext, binning=[40,0,40], histclass = ROOT.TH1F).make_hist()
        histos['SVdxySig'] = HistInfo(hname = 'SVdxySig', sample = histext, binning=[100,0,2500], histclass = ROOT.TH1F).make_hist()
        histos['SVmass'] = HistInfo(hname = 'SVmass', sample = histext, binning=[40,0,20], histclass = ROOT.TH1F).make_hist()
        histos['SVdlenSig'] = HistInfo(hname = 'SVdlenSig', sample = histext, binning=[100,0,2500], histclass = ROOT.TH1F).make_hist()
        histos['SVpAngle'] = HistInfo(hname = 'SVpAngle', sample = histext, binning=[40,0,4], histclass = ROOT.TH1F).make_hist()
        histos['SVpT'] = HistInfo(hname = 'SVpT', sample = histext, binning=[100,0,250], histclass = ROOT.TH1F).make_hist()
        histos['SVdR'] = HistInfo(hname = 'SVdR', sample = histext, binning=[40,0,4], histclass = ROOT.TH1F).make_hist()

        ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        FillHistos_IVF(histos, ch, options.year, options.nevents, sample, DataLumi, False).fill()
        hfile.Write()

else:
    for l in list(samplelist.values()):
        if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['nSV'] = HistInfo(hname = 'nSV', sample = histext, binning=[20,0,20], histclass = ROOT.TH1F).make_hist()
    histos['Ntracks'] = HistInfo(hname = 'Ntracks', sample = histext, binning=[20,0,20], histclass = ROOT.TH1F).make_hist()
    histos['SVdxy'] = HistInfo(hname = 'SVdxy', sample = histext, binning=[40,0,40], histclass = ROOT.TH1F).make_hist()
    histos['SVdxySig'] = HistInfo(hname = 'SVdxySig', sample = histext, binning=[100,0,2500], histclass = ROOT.TH1F).make_hist()
    histos['SVmass'] = HistInfo(hname = 'SVmass', sample = histext, binning=[40,0,20], histclass = ROOT.TH1F).make_hist()
    histos['SVdlenSig'] = HistInfo(hname = 'SVdlenSig', sample = histext, binning=[100,0,2500], histclass = ROOT.TH1F).make_hist()
    histos['SVpAngle'] = HistInfo(hname = 'SVpAngle', sample = histext, binning=[40,0,4], histclass = ROOT.TH1F).make_hist()
    histos['SVpT'] = HistInfo(hname = 'SVpT', sample = histext, binning=[100,0,250], histclass = ROOT.TH1F).make_hist()
    histos['SVdR'] = HistInfo(hname = 'SVdR', sample = histext, binning=[40,0,4], histclass = ROOT.TH1F).make_hist()

    ch = SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    FillHistos_IVF(histos, ch, options.year, options.nevents, sample, DataLumi, False).fill()
    hfile.Write()

#outputDir = os.getcwd()

bashline = []    

if 'Data' in samples:
    sLi = samples.replace('Data','')+'Run'
    bashline.append('hadd 1DHist_%s.root 1DHist_%s*.root\n'%(samples, sLi))
elif 'T2tt' in samples:
    bashline.append('hadd 1DHist_%s.root 1DHist_%s_*.root\n'%(samples, samples))
elif isinstance(samplelist[samples][0], types.ListType):
    sLi = 'hadd 1DHist_'+samples+'.root'+str("".join(' 1DHist_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[samples]))
    bashline.append('%s\n'%sLi)
else:
    bashline.append('hadd 1DHist_%s.root 1DHist_%s_*.root\n'%(samples, samples))
bashline.append('mv 1DHist_%s.root %s\n'%(samples, Rootfilesdirpath))


fsh = open("FileHandle.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 FileHandle.sh')
os.system('./FileHandle.sh')
os.system('rm *.root FileHandle.sh')

outputDir = plotDir
for key in histos:
    Plot1D(histos[key], outputDir, islogy=True)
