import os, sys
import ROOT
import types

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Helper.TreeVarSel_LL import TreeVarSel
from Helper.MCWeight import MCWeight
from Helper.VarCalc import *

def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='Sig_Prompt_500_420',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    

    return argParser

options = get_parser().parse_args()

fullsample  = options.sample+'_full'
fastsample  = options.sample+'_fast'
year = options.year
nevents = options.nevents

DataLumi=1.0


if year=='2016PreVFP':
        samplelist = samples_2016Pre
        DataLumi = SampleChain.luminosity_2016PreVFP
elif year=='2016PostVFP':
        samplelist = samples_2016Post
        DataLumi = SampleChain.luminosity_2016PostVFP
elif year=='2017':
        samplelist = samples_2017
        DataLumi = SampleChain.luminosity_2017
else:
        samplelist = samples_2018
        DataLumi = SampleChain.luminosity_2018
            

histext = ''
histext = fullsample
for l in list(samplelist.values()):
    if samplelist[fullsample] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
print 'running over: ', fullsample
hfile = ROOT.TFile('FastFullComp_'+fullsample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
histos = {}
histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
histos['Njet'] = HistInfo(hname = 'Njet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos['Nbjet'] = HistInfo(hname = 'Nbjet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
histos['lepPt'] = HistInfo(hname = 'lepPt', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
histos['lepdxy'] = HistInfo(hname = 'lepdxy', sample = histext, binning=[0,0.02,0.5,1,10], histclass = ROOT.TH1F, binopt = 'var').make_hist()
histos['HT'] = HistInfo(hname = 'HT', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['lepMT'] = HistInfo(hname = 'lepMT', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
histos['CT1'] = HistInfo(hname = 'CT1', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
histos['CT2'] = HistInfo(hname = 'CT2', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
ch = SampleChain(fullsample, options.startfile, options.nfiles, options.year).getchain()
print 'Total events of selected files of the', fullsample, 'fullsim sample: ', ch.GetEntries()
n_entries = ch.GetEntries()
nevtcut = n_entries -1 if nevents == - 1 else nevents - 1
print 'Running over total events: ', nevtcut+1
for ientry in range(n_entries):
    if ientry > nevtcut: break
    if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
    ch.GetEntry(ientry)
    lumiscale = (DataLumi/1000.0) * ch.weight
    MCcorr = MCWeight(ch, year, fullsample).getTotalWeight()

    getsel = TreeVarSel(ch, False, year)
    Fill1D(histos['MET'], ch.MET_pt, lumiscale)
    Fill1D(histos['Njet'], getsel.calNj(20), lumiscale)
    Fill1D(histos['Nbjet'], getsel.cntBtagjet(), lumiscale)
    Fill1D(histos['ISRJetPt'], getsel.getISRPt(), lumiscale)
    for l in getsel.getSortedLepVar():
        Fill1D(histos['lepPt'], l['pt'], lumiscale)
        Fill1D(histos['lepdxy'], l['dxy'], lumiscale)
    Fill1D(histos['HT'], getsel.calHT(), lumiscale)
    Fill1D(histos['lepMT'], getsel.getLepMT(), lumiscale)
    Fill1D(histos['CT1'], getsel.calCT(1), lumiscale)
    Fill1D(histos['CT2'], getsel.calCT(2), lumiscale)
hfile.Write()


histext2 = ''
histext2 = fastsample
for l in list(samplelist.values()):
    if samplelist[fastsample] in l: histext2 = list(samplelist.keys())[list(samplelist.values()).index(l)]
print 'running over: ', fastsample
hfile2 = ROOT.TFile('FastFullComp_'+fastsample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
histos2 = {}
histos2['MET'] = HistInfo(hname = 'MET', sample = histext2, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
histos2['Njet'] = HistInfo(hname = 'Njet20', sample = histext2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Nbjet'] = HistInfo(hname = 'Nbjet20', sample = histext2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext2, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
histos2['lepPt'] = HistInfo(hname = 'lepPt', sample = histext2, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
histos2['lepdxy'] = HistInfo(hname = 'lepdxy', sample = histext2, binning=[0,0.02,0.5,1,10], histclass = ROOT.TH1F, binopt = 'var').make_hist()
histos2['HT'] = HistInfo(hname = 'HT', sample = histext2, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['lepMT'] = HistInfo(hname = 'lepMT', sample = histext2, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
histos2['CT1'] = HistInfo(hname = 'CT1', sample = histext2, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['CT2'] = HistInfo(hname = 'CT2', sample = histext2, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
ch2 = SampleChain(fastsample, options.startfile, options.nfiles, options.year).getchain()
print 'Total events of selected files of the', fastsample, 'fastsim sample: ', ch2.GetEntries()
n_entries2 = ch2.GetEntries()
nevtcut2 = n_entries2 -1 if nevents == - 1 else nevents - 1
print 'Running over total events: ', nevtcut2+1
for ientry in range(n_entries2):
    if ientry > nevtcut2: break
    if ientry % (nevtcut2/10)==0 : print 'processing ', ientry,'th event'
    ch2.GetEntry(ientry)
    lumiscale = (DataLumi/1000.0) * ch2.weight
    MCcorr = MCWeight(ch2, year, fastsample).getTotalWeight()

    getsel = TreeVarSel(ch2, False, year)
    Fill1D(histos2['MET'], ch2.MET_pt, lumiscale)
    Fill1D(histos2['Njet'], getsel.calNj(20), lumiscale)
    Fill1D(histos2['Nbjet'], getsel.cntBtagjet(), lumiscale)
    Fill1D(histos2['ISRJetPt'], getsel.getISRPt(), lumiscale)
    for l in getsel.getSortedLepVar():
        Fill1D(histos2['lepPt'], l['pt'], lumiscale)
        Fill1D(histos2['lepdxy'], l['dxy'], lumiscale)
    Fill1D(histos2['HT'], getsel.calHT(), lumiscale)
    Fill1D(histos2['lepMT'], getsel.getLepMT(), lumiscale)
    Fill1D(histos2['CT1'], getsel.calCT(1), lumiscale)
    Fill1D(histos2['CT2'], getsel.calCT(2), lumiscale)
hfile2.Write()

#Plotting

Rootfilesdirpath = os.path.join(plotDir, "FastFullComp", options.year)
if not os.path.exists(Rootfilesdirpath): 
    os.makedirs(Rootfilesdirpath)
outputDir = os.path.join(Rootfilesdirpath, options.sample)

ffull = ROOT.TFile('FastFullComp_'+fullsample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root')
ffast = ROOT.TFile('FastFullComp_'+fastsample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root')

keysfull = [key.GetName() for key in ffull.GetListOfKeys()]
keysfast = [key.GetName() for key in ffast.GetListOfKeys()]

if len(keysfull) != len(keysfast):
        raise ValueError("Histograms don't match!")
else:
        for i in range(len(keysfull)):
            hfull = ffull.Get(keysfull[i])
            hfast = ffast.Get(keysfast[i])
            CompareHist(hfull, hfast, 'fastfull', outputDir, islogy=True, scaleOption='unitscaling')
