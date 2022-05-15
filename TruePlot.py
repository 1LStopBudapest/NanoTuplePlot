import ROOT
import types
import os, sys

from TrueFill import TrueFill

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Helper.VarCalc import *
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.Dir import plotDir


def get_parser():
    ''' Argument parser.'''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='Sig_Displaced_350_335',                          help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                    help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',          action='store',                     type=int,            default=-1,                                               help="No of events to run. -1 means all events" )

    return argParser

options = get_parser().parse_args()
sample  = options.sample
year = options.year

Rootfilesdirpath = os.path.join(plotDir, "1DFiles/truce")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

print 'running over: ', sample
hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
histos = {}
#coordinates
histos['gStop_dx'] = HistInfo(hname = 'gStop_dx', sample = sample, binning=[40,0.8,1.0], histclass = ROOT.TH1F).make_hist()
histos['gStop_dy'] = HistInfo(hname = 'gStop_dy', sample = sample, binning=[40,1.6,1.8], histclass = ROOT.TH1F).make_hist()
histos['gStop_dz'] = HistInfo(hname = 'gStop_dz', sample = sample, binning=[40,-15,15], histclass = ROOT.TH1F).make_hist()
histos['gVtx_dx'] = HistInfo(hname = 'gVtx_dx', sample = sample, binning=[40,0.8,1.0], histclass = ROOT.TH1F).make_hist()
histos['gVtx_dy'] = HistInfo(hname = 'gVtx_dy', sample = sample, binning=[40,1.6,1.8], histclass = ROOT.TH1F).make_hist()
histos['gVtx_dz'] = HistInfo(hname = 'gVtx_dz', sample = sample, binning=[40,-15,15], histclass = ROOT.TH1F).make_hist()
histos['gB_dx'] = HistInfo(hname = 'gB_dx', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist() #Prompt: [40,0.8,1]
histos['gB_dy'] = HistInfo(hname = 'gB_dy', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist() #Prompt: [40,1.6,1.8]
histos['gB_dz'] = HistInfo(hname = 'gB_dz', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
#distance
histos['gStop_gVtx_dx'] = HistInfo(hname = 'gStop_gVtx_dx', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gVtx_dy'] = HistInfo(hname = 'gStop_gVtx_dy', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gVtx_dz'] = HistInfo(hname = 'gStop_gVtx_dz', sample = sample, binning=[40,0,40], histclass = ROOT.TH1F).make_hist()
histos['gStop_gVtx_2D'] = HistInfo(hname = 'gStop_gVtx_2D', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gVtx_3D'] = HistInfo(hname = 'gStop_gVtx_3D', sample = sample, binning=[40,0,40], histclass = ROOT.TH1F).make_hist()
#
histos['gStop_gAStop_dx'] = HistInfo(hname = 'gStop_gAStop_dx', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gAStop_dy'] = HistInfo(hname = 'gStop_gAStop_dy', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gAStop_dz'] = HistInfo(hname = 'gStop_gAStop_dz', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gAStop_2D'] = HistInfo(hname = 'gStop_gAStop_2D', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['gStop_gAStop_3D'] = HistInfo(hname = 'gStop_gAStop_3D', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
#
histos['gLSP_gStop_dx'] = HistInfo(hname = 'gLSP_gStop_dx', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['gLSP_gStop_dy'] = HistInfo(hname = 'gLSP_gStop_dy', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['gLSP_gStop_dz'] = HistInfo(hname = 'gLSP_gStop_dz', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['gLSP_gStop_2D'] = HistInfo(hname = 'gLSP_gStop_2D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['gLSP_gStop_3D'] = HistInfo(hname = 'gLSP_gStop_3D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
#
histos['PV_gVtx_dx'] = HistInfo(hname = 'PV_gVtx_dx', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['PV_gVtx_dy'] = HistInfo(hname = 'PV_gVtx_dy', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['PV_gVtx_dz'] = HistInfo(hname = 'PV_gVtx_dz', sample = sample, binning=[40,0,100], histclass = ROOT.TH1F).make_hist()
histos['PV_gVtx_2D'] = HistInfo(hname = 'PV_gVtx_2D', sample = sample, binning=[40,0,1], histclass = ROOT.TH1F).make_hist()
histos['PV_gVtx_3D'] = HistInfo(hname = 'PV_gVtx_3D', sample = sample, binning=[40,0,100], histclass = ROOT.TH1F).make_hist()
#
histos['PV_gLSP_dx'] = HistInfo(hname = 'PV_gLSP_dx', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['PV_gLSP_dy'] = HistInfo(hname = 'PV_gLSP_dy', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['PV_gLSP_dz'] = HistInfo(hname = 'PV_gLSP_dz', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['PV_gLSP_2D'] = HistInfo(hname = 'PV_gLSP_2D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['PV_gLSP_3D'] = HistInfo(hname = 'PV_gLSP_3D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
#
histos['gVtx_gLSP_dx'] = HistInfo(hname = 'gVtx_gLSP_dx', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['gVtx_gLSP_dy'] = HistInfo(hname = 'gVtx_gLSP_dy', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['gVtx_gLSP_dz'] = HistInfo(hname = 'gVtx_gLSP_dz', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['gVtx_gLSP_2D'] = HistInfo(hname = 'gVtx_gLSP_2D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['gVtx_gLSP_3D'] = HistInfo(hname = 'gVtx_gLSP_3D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
#SV
histos['nSV'] = HistInfo(hname = 'nSV', sample = sample, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos['SV_gLSP_dx'] = HistInfo(hname = 'SV_gLSP_dx', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['SV_gLSP_dy'] = HistInfo(hname = 'SV_gLSP_dy', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['SV_gLSP_dz'] = HistInfo(hname = 'SV_gLSP_dz', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['SV_gLSP_2D'] = HistInfo(hname = 'SV_gLSP_2D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['SV_gLSP_3D'] = HistInfo(hname = 'SV_gLSP_3D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
#
histos['SV_gVtx_dx'] = HistInfo(hname = 'SV_gVtx_dx', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['SV_gVtx_dy'] = HistInfo(hname = 'SV_gVtx_dy', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['SV_gVtx_dz'] = HistInfo(hname = 'SV_gVtx_dz', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['SV_gVtx_2D'] = HistInfo(hname = 'SV_gVtx_2D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['SV_gVtx_3D'] = HistInfo(hname = 'SV_gVtx_3D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
#
histos['SV_gB_dx'] = HistInfo(hname = 'SV_gB_dx', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['SV_gB_dy'] = HistInfo(hname = 'SV_gB_dy', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['SV_gB_dz'] = HistInfo(hname = 'SV_gB_dz', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['SV_gB_2D'] = HistInfo(hname = 'SV_gB_2D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['SV_gB_3D'] = HistInfo(hname = 'SV_gB_3D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()



ch = SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
TrueFill(histos, ch, options.year, options.nevents, sample).fill()

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
