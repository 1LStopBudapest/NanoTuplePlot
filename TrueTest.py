import ROOT
import types
import os, sys

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Helper.VarCalc import *
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.Dir import plotDir
from Helper.TreeVarSel import TreeVarSel
from Helper.TreeVarSel_true import TreeVarSel_true
from Helper.IVFhelper import IVFhelper
from Helper.MCWeight import MCWeight



def get_parser():
    ''' Argument parser.'''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='Sig_Prompt_500_450_full',                             help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                    help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',          action='store',                     type=int,            default=-1,                                               help="No of events to run. -1 means all events" )

    return argParser

options = get_parser().parse_args()
sample  = options.sample
year = options.year

Rootfilesdirpath = os.path.join(plotDir, "1DFiles/efficiency_1130")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

print 'running over: ', sample
hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
histos = {}

#histos['gVtx_gLSP_3D_if'] = HistInfo(hname = 'gVtx_gLSP_3D_if', sample = sample, binning=[40,0,40], histclass = ROOT.TH1F).make_hist()
#histos['gVtx_gLSP_3D'] = HistInfo(hname = 'gVtx_gLSP_3D', sample = sample, binning=[40,0,40], histclass = ROOT.TH1F).make_hist()
#histos['SV_gLSP_3D'] = HistInfo(hname = 'SV_gLSP_3D', sample = sample, binning=[40,0,400], histclass = ROOT.TH1F).make_hist()
histos['pt_stop'] = HistInfo(hname = 'pt_stop', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['pt_b'] = HistInfo(hname = 'pt_b', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
#histos['pt_LSP_stop'] = HistInfo(hname = 'pt_LSP_stop', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()

#effi = ROOT.TEfficiency("eff", "Efficiency; d_{xyz}(genVtx,genLSP) [#mum]", 40,0,40) #mum
effi1 = ROOT.TEfficiency("eff1", "Efficiency; p_{T}(stop) [GeV]", 40,0,1000)
effi2 = ROOT.TEfficiency("eff2", "Efficiency; p_{T}(b) [GeV] [GeV]", 40,0,1000)


keylist = ['gVtx_gLSP_dx', 'gVtx_gLSP_dy', 'gVtx_gLSP_dz', 'gVtx_gLSP_2D', 'gVtx_gLSP_3D',
           'SV_gLSP_dx', 'SV_gLSP_dy', 'SV_gLSP_dz', 'SV_gLSP_2D', 'SV_gLSP_3D',
           'gVtx_gLSP_3D_if', 'pt_stop', 'pt_LSP_stop', 'pt_b']
vardic = {key: None for key in keylist}


ch = SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
n_entries = ch.GetEntries()
nevtcut = n_entries -1 if options.nevents == - 1 else options.nevents - 1

for ientry in range(n_entries):
    if ientry > nevtcut: break
    if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
    ch.GetEntry(ientry) 
    getsel = TreeVarSel(ch, False, year)
    getselT = TreeVarSel_true(ch, year)
    getivf = IVFhelper(ch, False, year)
    var = {key: None for key in vardic}
    MCcorr = MCWeight(ch, year, sample).getTotalWeight()

    #genVtx = getselT.getGenVtx()
    #genLSP_S = getselT.getLSP_S()
    #genLSP_A = getselT.getLSP_A()
    #sv = getivf.getSV()

    boo = False
    #boo2 = False
    if getsel.PreSelection() and getsel.cntBtagjet(pt=0)==0:
        var['pt_stop'] = getselT.getStopPt()
        var['pt_b'] = getselT.getBPt()
        if getivf.IVFSelection() and getivf.HadronicSelection(): #nevezo
            boo = True
        effi1.Fill(boo, var['pt_stop'])
        effi2.Fill(boo, var['pt_b'])
    '''
        var['pt_stop'] = getselT.getStopPt()
        var['pt_LSP_stop'] = getselT.getLSPStopPt()
    if len(genLSP_S) > 0 and len(genLSP_A) > 0:
            var['gVtx_gLSP_dx'] = [getselT.distance(genLSP_S, genVtx, 'x')*10000, getselT.distance(genLSP_A, genVtx, 'x')*10000] #d*10000 <--> Prompt #mum
            var['gVtx_gLSP_dy'] = [getselT.distance(genLSP_S, genVtx, 'y')*10000, getselT.distance(genLSP_A, genVtx, 'y')*10000]
            var['gVtx_gLSP_dz'] = [getselT.distance(genLSP_S, genVtx, 'z')*10000, getselT.distance(genLSP_A, genVtx, 'z')*10000]
        var['gVtx_gLSP_2D'] = [sqrt(var['gVtx_gLSP_dx'][i]**2 + var['gVtx_gLSP_dy'][i]**2) for i in range(2)]
        var['gVtx_gLSP_3D'] = [sqrt(var['gVtx_gLSP_dx'][i]**2 + var['gVtx_gLSP_dy'][i]**2 + var['gVtx_gLSP_dz'][i]**2) for i in range(2)]
        if len(sv) >= 1:
            if len(sv) > 1:
                    var['SV_gLSP_3D'] = getselT.smallestUniqueDist3D([genLSP_S, genLSP_A], sv)
            elif len(sv) == 1:
                    var['SV_gLSP_3D'] = getselT.only1SV(genLSP_S, genLSP_A, sv)

                var['gVtx_gLSP_3D_if'] = []
                if var['SV_gLSP_3D'][0] < 0.1: #1 mm
                    var['gVtx_gLSP_3D_if'].append(var['gVtx_gLSP_3D'][0])
                    boo1 = True
                if var['SV_gLSP_3D'][1] < 0.1:  
                    var['gVtx_gLSP_3D_if'].append(var['gVtx_gLSP_3D'][1])
                    boo2 = True
                effi.Fill(boo1, var['gVtx_gLSP_3D'][0])
                effi.Fill(boo2, var['gVtx_gLSP_3D'][1])

                if var['gVtx_gLSP_3D'][0] < 4 and var['gVtx_gLSP_3D'][1] < 4: #4 mum
                    effi1.Fill(boo1 or boo2, var['pt_stop'])
                    effi2.Fill(boo1 or boo2, var['pt_LSP_stop'])
    '''

#if (ROOT.TEfficiency.CheckConsistency(histos['gVtx_gLSP_3D_if'], histos['gVtx_gLSP_3D'])):
#    effi = ROOT.TEfficiency(histos['gVtx_gLSP_3D_if'], histos['gVtx_gLSP_3D'])
#effi = ROOT.TGraphAsymmErrors.Divide(histos['gVtx_gLSP_3D_if'], histos['gVtx_gLSP_3D'])

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
outputdirpath = os.path.join(plotDir, "1DPlots/efficiency_1130")
#for key in histos:
#    Plot1D(histos[key], outputDir, islogy=True)

#Plot1D(histos['pt_stop'], outputDir, islogy=True)
#Plot1D(histos['pt_b'], outputDir, islogy=True)

if not os.path.exists(outputdirpath):
    os.makedirs(outputdirpath)
def plotEfficiency(eff, name):
    leg = ROOT.TLegend(0.5, 0.85, 0.9, 0.9)
    leg.AddEntry(eff, sample ,"l")
    c = ROOT.TCanvas('c', '', 600, 600)
    c.SetFillStyle(1001)
    c.SetFillColor(ROOT.kWhite)
    c.cd()
    eff.Draw()
    ROOT.gPad.Update()
    #graph = eff.GetPaintedGraph()
    #graph.SetMinimum(0.0)
    #graph.SetMaximum(0.3)
    #ROOT.gPad.Update()
    leg.Draw("SAMES")
    c.SaveAs(outputdirpath+"/"+name+".png")
    c.Close()

#plotEfficiency(effi, "efficiency")
plotEfficiency(effi1, "efficiency_stop")
plotEfficiency(effi2, "efficiency_b")
