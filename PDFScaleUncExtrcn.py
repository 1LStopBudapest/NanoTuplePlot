import os, sys
import ROOT



sys.path.append('../')
from Sample.Dir import plotDir
from Helper.PlotHelper import *


outputdirpath = os.path.join(plotDir,"PDFScaleFiles")
if not os.path.exists(outputdirpath):
    os.makedirs(outputdirpath)

year = '2017'
bins = 108 + 24 #SRbins
hScale = {}
hPDF = {}
sname = ['Sig_Prompt_500_420_fast', 'Sig_Prompt_500_450_fast', 'Sig_Prompt_500_470_fast']
#sname = ['Sig_Prompt_500_420_fast']
for s in sname:
    fname = 'PDFScaleUnc_SR+CR_'+s+'_1_-1.root'
    f = None
    getval = True

    if os.path.exists(fname):
        f = ROOT.TFile.Open(fname)
    elif os.path.exists(outputdirpath+'/'+fname):
        f = ROOT.TFile.Open(outputdirpath+'/'+fname)
    else:
        getval = False        
        print 'Root file ',fname,' does not exist. Please run python PDFScaleUnc.py --sample',s


    if getval :
        PDFVar = 103
        ScaleVar = 9
        histosPDF = []
        histosScale = []
        hsm = f.Get('h_rate_'+s)
        hpm = hsm.Clone('h_pdf')
        for i in range(ScaleVar):
            histosScale.append(f.Get('h_rateScale_'+str(i)+'_'+s))
        for i in range(PDFVar):
            histosPDF.append(f.Get('h_ratePDF_'+str(i)+'_'+s))

        hsRatio = []
        hsNorm = []
        for hs in histosScale:
            hsRatio.append(getHistratio(hs, hsm, 'Scale Variation', 'SR Bins'))
            hsNorm.append(hsm.Integral()/hs.Integral())
        for i, hsr in enumerate(hsRatio):
            hsr.Scale(hsNorm[i])
            
        hpRatio = []
        hpNorm = []
        for hp in histosPDF:
            hpRatio.append(getHistratio(hp, hpm, 'PDF Variation', 'SR Bins'))
            hpNorm.append(hpm.Integral()/hp.Integral())
        for i, hpr in enumerate(hpRatio):
            hpr.Scale(hpNorm[i])
            
        mls = []
        mlp = []
        for b in range(bins):
            ls = []
            for hsr in hsRatio:
                ls.append(abs(1-hsr.GetBinContent(b+1)))
            lp = []  
            for hpr in hpRatio:
                lp.append(abs(1-hpr.GetBinContent(b+1)))

            mls.append(max(ls))
            mlp.append(max(lp))

        #print len(mls), mls
        #print len(mlp), mlp
    hScale[s] = mls
    hPDF[s] = mlp

als = []
alp = []
for b in range(bins):
    asc = 0
    ap = 0
    for k in hScale:
       asc=asc+hScale[k][b]
       ap=ap+hPDF[k][b]
    als.append(round(asc/len(hScale), 3))
    alp.append(round(ap/len(hPDF), 3))
print len(als), als
print len(alp), alp
hfile = ROOT.TFile(outputdirpath+'/PDFScaleUnc_FastsimSig_'+year+'.root', 'RECREATE')
hscale = ROOT.TH1F('hscale', 'hscale', bins, 0, bins)
hPDF = ROOT.TH1F('hPDF', 'hPDF', bins, 0, bins)
for b in range(bins):
    hscale.SetBinContent(b+1, als[b])
    hPDF.SetBinContent(b+1, alp[b])
hfile.Write()
