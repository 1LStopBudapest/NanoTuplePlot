import ROOT
import types
import os, sys

sys.path.append('../')
from Helper.VarCalc import *
from Helper.TreeVarSel_true import TreeVarSel
from Helper.MCWeight import MCWeight
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir


def get_parser():
    ''' Argument parser.'''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='UL17V9_Full99mm',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',          action='store',                     type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    
    return argParser

options = get_parser().parse_args()

keylist = ['gStop_gVtx_dx', 'gStop_gVtx_dy', 'gStop_gVtx_dz']

tr = SampleChain(options.sample, options.startfile, options.nfiles, options.year).getchain() 
lumiscale = 1.0 #???
MCcorr = MCWeight(tr, options.year, options.sample).getTotalWeight()


Rootfilesdirpath = os.path.join(plotDir, "1DFiles/truce")
if not os.path.exists(Rootfilesdirpath): 
    os.makedirs(Rootfilesdirpath)

sample = options.sample
print 'running over: ', sample
hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
histos = {}
histos['gStop_gVtx_dx'] = HistInfo(hname = 'gStop_gVtx_dx', sample = sample, binning=[40,-1,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gVtx_dy'] = HistInfo(hname = 'gStop_gVtx_dy', sample = sample, binning=[40,-1,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gVtx_dz'] = HistInfo(hname = 'gStop_gVtx_dz', sample = sample, binning=[40,0,40], histclass = ROOT.TH1F).make_hist()

ch = SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()


n_entries = tr.GetEntries()
nevtcut = n_entries -1 if options.nevents == - 1 else options.nevents - 1
print 'Running over total events: ', nevtcut+1
vardic = {key: None for key in keylist}

for ientry in range(n_entries):
    if ientry > nevtcut: break
    if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
    tr.GetEntry(ientry) #ientry = i. event 
    getsel = TreeVarSel(tr=tr, isData=False, yr=options.year)
    var = {key: None for key in vardic} #reseting the var dictionary for each event

    genStop = getsel.getGenPartStop()
    genVtx = getsel.getGenVtx()

    var['gStop_gVtx_dx'] = getsel.xDist(genVtx, genStop[0], 'x')*10000 # original is in cm, right?
    var['gStop_gVtx_dy'] = getsel.xDist(genVtx, genStop[0], 'y')*10000 # ==> um
    var['gStop_gVtx_dz'] = getsel.xDist(genVtx, genStop[0], 'z')*10000

    for key in keylist:
        if var[key] is not None:
            if isinstance(var[key], types.ListType):
                for x in var[key]: 
                    Fill1D(histos[key], x, lumiscale * MCcorr)
            else:
                Fill1D(histos[key], var[key], lumiscale * MCcorr)

hfile.Write()
bashline = []    
bashline.append('hadd 1DHist_%s.root 1DHist_%s_*.root\n'%(sample, sample))
bashline.append('mv 1DHist_%s.root %s\n'%(sample, Rootfilesdirpath))

fsh = open("FileHandle.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 FileHandle.sh')
os.system('./FileHandle.sh')
os.system('rm *.root FileHandle.sh')

outputDir = plotDir
for key in histos:
    Plot1D(histos[key], outputDir, islogy=True)
