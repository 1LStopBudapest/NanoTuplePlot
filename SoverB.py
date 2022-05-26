import os, sys
import ROOT
import math


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir


def get_parser():
    ''' Argument parser.                                                                                                                                                
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument(
    '-lb', '--BKsamplelist',                 # either of this switches
    nargs='+',                              
    type=str,                               
    dest='blist',                           # store in 'list'.
    default=['ZJetsToNuNu', 'WJetsToLNu', 'DYJetsToLL', 'QCD', 'TTV', 'TTbar', 'ST', 'VV'], #'TTSingleLep_pow', 'TTLep_pow'
    )
    argParser.add_argument(
    '-ls', '--Sigsamplelist',                 # either of this switches
    nargs='+',                              
    type=str,                               
    dest='slist',                           # store in 'list'.
    default=['Sig_Displaced_350_335'],
    )
    argParser.add_argument(
    '-lcut', '--cutlist',                 # either of this switches
    nargs='+',                              
    type=str,                               
    dest='clist',                           # store in 'list'.
    default=['default', 'new'], # default: SR1: 0 b jets, SR2: 0 hard, >= 1 soft b jets
    # new: SR: 0 hard or soft b jets in both, but >= 1 SV jets
    )
    argParser.add_argument('--sel',            action='store',                    type=str,            default='bJets',          help="Which selection tag" )
    return argParser

options = get_parser().parse_args()

BKlists = options.blist
Siglists = options.slist
Cutlists = options.clist
seltag = options.sel

outputdirpath = os.path.join(plotDir, "SoverBPlots", seltag)
if not os.path.exists(outputdirpath):
    if os.path.exists(os.path.join(plotDir,"SoverBPlots")):
        os.mkdir(outputdirpath)
    else:
        os.makedirs(outputdirpath)

hsb_cut={}
hsspb_cut={}

hsb_cut_sig={}
hsspb_cut_sig={}

s = Siglists[0] #now only one signal point in one canvas
for cut in Cutlists:
    hbk=[]
    for bk in BKlists:
        f=ROOT.TFile.Open(plotDir+'RegionFiles/'+cut+'/RegionPlot_SR_'+bk+'.root')
        ROOT.TH1.AddDirectory(0)
        hbk.append(f.Get('h_reg_'+bk))
    fs=ROOT.TFile.Open(plotDir+'RegionFiles/'+cut+'/RegionPlot_SR_'+s+'.root')
    ROOT.TH1.AddDirectory(0)
    hsigx =fs.Get('h_reg_'+s)

    htot = hbk[0].Clone("TotalBK")
    for h in hbk[1:]:
        htot.Add(h)
    del hbk
    hsb = hsigx.Clone('hSB')
    hsb.Divide(htot)
    hspb = hsigx.Clone('hSpB')
    hspb.Add(htot)
    for b in range(hspb.GetNbinsX()):
        hspb.SetBinContent(b+1, math.sqrt(hspb.GetBinContent(b+1)))
    hsspb = hsigx.Clone('hSSpB')
    hsspb.Divide(hspb)
    hsb_cut[cut] = hsb
    hsspb_cut[cut] = hsspb


ROOT.gStyle.SetErrorX(0)
ROOT.gStyle.SetOptStat(0)
c = ROOT.TCanvas('c', '', 1400, 1000)
c.Divide(2,1)
c.cd(1)
leg1 = ROOT.TLegend(0.7, 0.8, 0.9, 0.9)
for i, cut in enumerate(hsb_cut):
    leg1.AddEntry(hsb_cut[cut], cut ,"l")
    hsb_cut[cut].SetLineColor(i+1)
    hsb_cut[cut].SetLineWidth(2)
    if i==0:
        hsb_cut[cut].SetTitle(s)
        hsb_cut[cut].GetYaxis().SetTitle('#frac{S}{B}')
        hsb_cut[cut].GetYaxis().SetTitleSize(0.035)
        hsb_cut[cut].GetYaxis().SetTitleOffset(1.2)
        hsb_cut[cut].GetYaxis().SetLabelSize(0.03)
        hsb_cut[cut].Draw('hist')
        hsb_cut[cut].LabelsOption('v')        
    else:
        hsb_cut[cut].Draw('histsame')
leg1.Draw('same')
c.cd(2)
leg2 = ROOT.TLegend(0.7, 0.8, 0.9, 0.9)
for i, cut in enumerate(hsspb_cut):
    leg2.AddEntry(hsspb_cut[cut], cut ,"l")
    hsspb_cut[cut].SetLineColor(i+1)
    hsspb_cut[cut].SetLineWidth(2)
    if i==0:
        hsspb_cut[cut].SetTitle(s)
        hsspb_cut[cut].GetYaxis().SetTitle('#frac{S}{#sqrt{S+B}}')
        hsspb_cut[cut].GetYaxis().SetTitleSize(0.035)
        hsspb_cut[cut].GetYaxis().SetTitleOffset(1.2)
        hsspb_cut[cut].GetYaxis().SetLabelSize(0.03)
        hsspb_cut[cut].Draw('hist')
        hsspb_cut[cut].LabelsOption('v')  
    else:
        hsspb_cut[cut].Draw('histsame')
leg2.Draw('same')

c.SaveAs(outputdirpath+"/SIGoverBK.png")
c.Close()
hsb_cut.clear()
hsspb_cut.clear()


