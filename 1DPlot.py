import os, sys
import ROOT
import types

from FillHistos import FillHistos

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTSingleLep_pow',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    

    return argParser

options = get_parser().parse_args()

samples  = options.sample
year = options.year

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
            
#vList = ['MET', 'ISRJetPt', 'HT', 'LepMT', 'CT1', 'CT2', 'Njet', 'Nbjet', 'LeppT']
#vList = ['LeppT', 'MupT', 'epT']
vList = ['LeppT']

histext = ''

sdir = '1DFiles/'+year
Rootfilesdirpath = os.path.join(plotDir, sdir)
if not os.path.exists(Rootfilesdirpath): 
    os.makedirs(Rootfilesdirpath)

    
if 'T2tt' in samples:
    sample = samples
    histext = samples
    print 'running over: ', sample
    hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    '''
    histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
    histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['HT'] = HistInfo(hname = 'HT', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['LepMT'] = HistInfo(hname = 'LepMT', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
    histos['CT1'] = HistInfo(hname = 'CT1', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['CT2'] = HistInfo(hname = 'CT2', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['Njet'] = HistInfo(hname = 'Njet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    histos['Nbjet'] = HistInfo(hname = 'Nbjet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    '''
    histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[50,0,200], histclass = ROOT.TH1F).make_hist()
    '''
    histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['MupT'] = HistInfo(hname = 'MupT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['epT'] = HistInfo(hname = 'epT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    '''
    ch = SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    FillHistos(histos, ch, options.year, options.nevents, sample, vList, DataLumi, False).fill()
    hfile.Write()
else:
    if isinstance(samplelist[samples][0], types.ListType):
        histext = samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
            histos = {}
            '''
            histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
            histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
            histos['HT'] = HistInfo(hname = 'HT', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
            histos['LepMT'] = HistInfo(hname = 'LepMT', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
            histos['CT1'] = HistInfo(hname = 'CT1', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
            histos['CT2'] = HistInfo(hname = 'CT2', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
            histos['Njet'] = HistInfo(hname = 'Njet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
            histos['Nbjet'] = HistInfo(hname = 'Nbjet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
            '''
            histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[50,0,200], histclass = ROOT.TH1F).make_hist()
            '''
            histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
            histos['MupT'] = HistInfo(hname = 'MupT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
            histos['epT'] = HistInfo(hname = 'epT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
            '''
            ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
            print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
            FillHistos(histos, ch, options.year, options.nevents, sample, vList, DataLumi, False).fill()
            hfile.Write()

    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        '''
        histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
        histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
        histos['HT'] = HistInfo(hname = 'HT', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
        histos['LepMT'] = HistInfo(hname = 'LepMT', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
        histos['CT1'] = HistInfo(hname = 'CT1', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
        histos['CT2'] = HistInfo(hname = 'CT2', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
        histos['Njet'] = HistInfo(hname = 'Njet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
        histos['Nbjet'] = HistInfo(hname = 'Nbjet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
        '''
        histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[50,0,200], histclass = ROOT.TH1F).make_hist()
        '''
        histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['MupT'] = HistInfo(hname = 'MupT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['epT'] = HistInfo(hname = 'epT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        '''
        ch = SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        FillHistos(histos, ch, options.year, options.nevents, sample, vList, DataLumi, False).fill()
        hfile.Write()

'''
#outputDir = os.getcwd()
outputDir = Rootfilesdirpath
for key in histos:
    Plot1D(histos[key], outputDir, islogy=True)
    
'''
'''
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

fname = '1DHist_'+samples+'.root'
outputDir = Rootfilesdirpath
for var in vList:
    Plot1DExt(var, histext, fname, outputDir, islogy=True)
'''
