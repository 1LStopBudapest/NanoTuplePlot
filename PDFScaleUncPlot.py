import os, sys
import ROOT



sys.path.append('../')
from Sample.Dir import plotDir
from Helper.PlotHelper import *

def get_parser():
    ''' Argument parser.                                                                                                                                               
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--ifile',           action='store',                     type=str,            default='PDFScaleUnc_SR_Sig_Prompt_500_420_fast_1_-1.root',   help ="Which file?" )
    argParser.add_argument('--sample',           action='store',                     type=str,            default='Sig_Prompt_500_420_fast',   help ="Which sample?" )
    return argParser

options = get_parser().parse_args()

filename = options.ifile
sample = options.sample

outputdirpath = os.path.join(plotDir,"PDFScaleFiles")
if not os.path.exists(outputdirpath):
    os.makedirs(outputdirpath)
    
f = None
doplots = True

if os.path.exists(filename):
    f = ROOT.TFile.Open(filename)
elif os.path.exists(outputdirpath+filename):
    f = ROOT.TFile.Open(outputdirpath+filename)
else:
    doplots = False        
    print 'Root file ',filename,' does not exist. Please run python PDFScaleUnc.py --sample',sample


if doplots :
    PDFVar = 103
    ScaleVar = 9
    histosPDF = []
    histosScale = []
    hsm = f.Get('h_rate_'+sample)
    hpm = hsm.Clone('h_pdf')
    for i in range(ScaleVar):
        histosScale.append(f.Get('h_rateScale_'+str(i)+'_'+sample))
    for i in range(PDFVar):
        histosPDF.append(f.Get('h_ratePDF_'+str(i)+'_'+sample))

    hsRatio = []
    hsNorm = []
    for hs in histosScale:
        hsRatio.append(getHistratio(hs, hsm, 'Scale Variation', 'SR Bins'))
        hsNorm.append(hsm.Integral()/hs.Integral())
    hsRatioFrame = getHistratioframe(hsRatio[0])

    hpRatio = []
    hpNorm = []
    for hp in histosPDF:
        hpRatio.append(getHistratio(hp, hpm, 'PDF Variation', 'SR Bins'))
        hpNorm.append(hpm.Integral()/hp.Integral())
    hpRatioFrame = getHistratioframe(hpRatio[0])

    hsm.SetTitle("QCD Scale Variation")
    hsm.GetYaxis().SetTitle('Events')
    hsm.GetXaxis().SetTitle('SR')
    hsm.SetMarkerSize(0.5)
    hsm.SetMarkerStyle(20)
    hsm.SetMarkerColor(ROOT.kGreen)
    hsm.SetLineColor(ROOT.kGreen)
    hsm.SetLineWidth(2)
    hsm.SetLineStyle(2)
    hsm.SetStats(0)
    maxRange = hsm.GetBinContent(hsm.GetMaximumBin())
    hsm.GetYaxis().SetRangeUser(0.0 , maxRange*1.5)

    hpm.SetTitle("PDF Variation")
    hpm.GetYaxis().SetTitle('Events')
    hpm.GetXaxis().SetTitle('SR')
    hpm.SetMarkerSize(0.5)
    hpm.SetMarkerStyle(20)
    hpm.SetMarkerColor(ROOT.kGreen)
    hpm.SetLineColor(ROOT.kGreen)
    hpm.SetLineWidth(2)
    hpm.SetLineStyle(2)
    hpm.SetStats(0)
    maxRange = hpm.GetBinContent(hpm.GetMaximumBin())
    hpm.GetYaxis().SetRangeUser(0.0 , maxRange*1.5)

    #Scale Draw
    c1 = ROOT.TCanvas('c1', '', 1200, 800)
    p11 = ROOT.TPad("p11", "p11", 0, 0.3, 1, 1.0)
    p11.SetBottomMargin(0) # Upper and lower plot are joined
    p11.Draw()             # Draw the upper pad: p1
    p11.cd()
    hsm.Draw('hist')
    for hs in histosScale:
        hs.SetTitle("")
        hs.SetMarkerSize(0.5)
        hs.SetMarkerStyle(20)
        hs.SetMarkerColor(ROOT.kRed)
        hs.SetStats(0)
        hs.Draw('hist p SAME')
    c1.cd()
    p12 = ROOT.TPad("p12", "p12", 0, 0.01, 1, 0.3)
    p12.SetTopMargin(0)
    p12.SetBottomMargin(0.2)
    p12.Draw()
    p12.cd()
    hsRatioFrame.Draw("HIST")
    hsRatioFrame.GetYaxis().SetRangeUser(0.95,1.05)
    for i, hsr in enumerate(hsRatio):
        hsr.SetMarkerSize(0.4)
        hsr.SetMarkerColor(ROOT.kRed)
        hsr.SetMarkerStyle(20)
        hsr.Scale(hsNorm[i])
        hsr.Draw('hist p SAME')
    c1.SaveAs(outputdirpath+"/QCDScaleVariation_"+sample+".png")
    c1.Close()

    #PDF Draw
    c2= ROOT.TCanvas('c2', '', 1200, 800)
    p21 = ROOT.TPad("p21", "p21", 0, 0.3, 1, 1.0)
    p21.SetBottomMargin(0) # Upper and lower plot are joined
    p21.Draw()             # Draw the upper pad: p1
    p21.cd()
    hpm.Draw('hist')
    for hp in histosPDF:
        hp.SetTitle("")
        hp.SetMarkerSize(0.5)
        hp.SetMarkerStyle(20)
        hp.SetMarkerColor(ROOT.kRed)
        hp.SetStats(0)
        hp.Draw('hist p SAME')
    c2.cd()
    p22 = ROOT.TPad("p22", "p22", 0, 0.01, 1, 0.3)
    p22.SetTopMargin(0)
    p22.SetBottomMargin(0.2)
    p22.Draw()
    p22.cd()
    hpRatioFrame.Draw("HIST")
    hpRatioFrame.GetYaxis().SetRangeUser(0.95,1.05)
    for i, hpr in enumerate(hpRatio):
        hpr.SetMarkerSize(0.4)
        hpr.SetMarkerColor(ROOT.kRed)
        hpr.SetMarkerStyle(20)
        hpr.Scale(hpNorm[i])
        hpr.Draw('hist p SAME')
    c2.SaveAs(outputdirpath+"/PDFVariation_"+sample+".png")
    c2.Close()

          
