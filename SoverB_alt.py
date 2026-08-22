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
    default=['ZJetsToNuNu', 'WJetsToLNu', 'DYJetsToLL', 'QCD', 'TTV', 'TTbar', 'ST', 'VV'], 
    )
    argParser.add_argument(
    '-ls', '--Sigsamplelist',                 # either of this switches
    nargs='+',                              
    type=str,                               
    dest='slist',                           # store in 'list'.
    default=['Sig_Displaced_350_335_full', 'Sig_Displaced_400_380_full', 'Sig_Displaced_300_290_full'],
    )
    argParser.add_argument('--reg',            action='store',                    type=str,            default='SR+CR',          help="Which region" )
    return argParser

options = get_parser().parse_args()

BKlists = options.blist
Siglists = options.slist
reg = options.reg

outputdirpath = os.path.join(plotDir, "LLSoverBPlots")
if not os.path.exists(outputdirpath):
        os.mkdir(outputdirpath)


hsb_sig={}
hsspb_sig={}


hbk=[]
for bk in BKlists:
    f=ROOT.TFile.Open(plotDir+'LLDCFiles/LLCountDCHist_'+reg+'_'+bk+'.root')
    ROOT.TH1.AddDirectory(0)
    hbk.append(f.Get('h_rate_'+bk))

htot = hbk[0].Clone("TotalBK")
for h in hbk[1:]:
    htot.Add(h)
del hbk
    

for s in Siglists:
    fs=ROOT.TFile.Open(plotDir+'LLDCFiles/LLCountDCHist_'+reg+'_'+s+'.root')
    ROOT.TH1.AddDirectory(0)
    hsigx =fs.Get('h_rate_'+s)

    hsb = hsigx.Clone('hSB')
    hsb.Divide(htot)
    
    hspb = hsigx.Clone('hSpB')
    hspb.Add(htot)
    for b in range(hspb.GetNbinsX()):
        hspb.SetBinContent(b+1, math.sqrt(hspb.GetBinContent(b+1)))
    hsspb = hsigx.Clone('hSSpB')
    hsspb.Divide(hspb)
    hsb_sig[s] = hsb
    hsspb_sig[s] = hsspb

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetErrorX(0)
ROOT.gStyle.SetOptStat(0)
c1 = ROOT.TCanvas('c1', '', 1400, 1000)
c1.cd()
leg1 = ROOT.TLegend(0.7, 0.8, 0.9, 0.9)
for i, sig in enumerate(hsb_sig):
    leg1.AddEntry(hsb_sig[sig], sig ,"l")
    hsb_sig[sig].SetLineColor(i+1)
    hsb_sig[sig].SetLineWidth(2)
    if i==0:
        hsb_sig[sig].SetTitle('S/B')
        hsb_sig[sig].GetYaxis().SetTitle('#frac{S}{B}')
        hsb_sig[sig].GetYaxis().SetTitleSize(0.035)
        hsb_sig[sig].GetYaxis().SetTitleOffset(1.2)
        hsb_sig[sig].GetYaxis().SetLabelSize(0.03)
        hsb_sig[sig].Draw('hist')
        hsb_sig[sig].LabelsOption('v')        
    else:
        hsb_sig[sig].Draw('histsame')
leg1.Draw('same')
c1.SaveAs(outputdirpath+"/SIGoverBK_1.png")
c1.Close()

c2 = ROOT.TCanvas('c2', '', 1400, 1000)
c2.cd()
leg2 = ROOT.TLegend(0.7, 0.8, 0.9, 0.9)
ROOT.gPad.SetLogy()
for i, sig in enumerate(hsspb_sig):
    leg2.AddEntry(hsspb_sig[sig], sig ,"l")
    hsspb_sig[sig].SetLineColor(i+1)
    hsspb_sig[sig].SetLineWidth(2)
    if i==0:
        hsspb_sig[sig].SetTitle("S/#sqrt{S+B}")
        hsspb_sig[sig].GetYaxis().SetTitle('#frac{S}{#sqrt{S+B}}')
        hsspb_sig[sig].GetYaxis().SetTitleSize(0.035)
        hsspb_sig[sig].GetYaxis().SetTitleOffset(1.5)
        hsspb_sig[sig].GetYaxis().SetLabelSize(0.03)
        hsspb_sig[sig].Draw('hist')
        hsspb_sig[sig].LabelsOption('v')  
    else:
        hsspb_sig[sig].Draw('histsame')
leg2.Draw('same')
c2.SaveAs(outputdirpath+"/SIGoverBK_2.png")
c2.Close()

hsb_sig.clear()
hsspb_sig.clear()


