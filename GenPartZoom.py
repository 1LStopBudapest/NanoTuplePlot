import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Helper.HistInfo import HistInfo
from Helper.VarCalc import *

sample = 'Stop_500_480_fast'
startfile = 0
nfiles = -1
nEvents = -1



tr = SampleChain(sample, startfile, nfiles).getchain()
histos = {}
histos['GenMuonpt'] = HistInfo(hname = 'GenMuonpt', sample = sample, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
histos['GenStoppt'] = HistInfo(hname = 'GenStoppt', sample = sample, binning=[50,0,1000], histclass = ROOT.TH1F).make_hist()
histos['GenLSPpt'] = HistInfo(hname = 'GenLSPpt', sample = sample, binning=[50,0,1000], histclass = ROOT.TH1F).make_hist()
histos['GenBpt'] = HistInfo(hname = 'GenBpt', sample = sample, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()

histos['GenMustatus'] = HistInfo(hname = 'GenMustatus', sample = sample, binning=[15,10,25], histclass = ROOT.TH1F).make_hist()

n_entries = tr.GetEntries()

for ientry in range(n_entries):
    if not nEvents == -1 and ientry > nEvents - 1: break
    tr.GetEntry(ientry)

    #print 'event: ', ientry+1

    #for i in range(tr.nGenJet):
     #   print tr.GenJet_partonFlavour[i] 

    for i in range(tr.nGenPart):
        if abs(tr.GenPart_pdgId[i]) ==13 and GenFlagString(tr.GenPart_statusFlags[i])[-1]=='1' and tr.GenPart_genPartIdxMother[i] != -1:
            if tr.GenPart_status[i]==1:
                #if abs(tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[i]])==21 and tr.GenPart_genPartIdxMother[tr.GenPart_genPartIdxMother[i]] != -1:
                    #print 'mu mother flag: ', tr.GenPart_statusFlags[tr.GenPart_genPartIdxMother[i]], 'mu grand flag: ', tr.GenPart_statusFlags[tr.GenPart_genPartIdxMother[tr.GenPart_genPartIdxMother[i]]], 'mu grand pdgid: ', tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[tr.GenPart_genPartIdxMother[i]]]
                #if abs(tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[tr.GenPart_genPartIdxMother[i]]])!=24:
                    #print 'mu grand pdgid: ', tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[tr.GenPart_genPartIdxMother[i]]]
                    #for j in range(tr.nGenPart):
                     #   print 'particle idx: ', j, 'pdgID: ', tr.GenPart_pdgId[j], 'flag: ', tr.GenPart_statusFlags[j], 'status: ', tr.GenPart_status[j], 'mother idx: ', tr.GenPart_genPartIdxMother[j]

                Fill1D(histos['GenMuonpt'], tr.GenPart_pt[i])
                Fill1D(histos['GenMustatus'], abs(tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[i]]))
                
        if abs(tr.GenPart_pdgId[i])==1000006 and GenFlagString(tr.GenPart_statusFlags[i])[-1]=='1' and GenFlagString(tr.GenPart_statusFlags[i])[1]=='1' and GenFlagString(tr.GenPart_statusFlags[i])[6]=='1' and  GenFlagString(tr.GenPart_statusFlags[i])[3]=='1':
            #if tr.GenPart_status[i]!=62: print tr.GenPart_status[i]
            Fill1D(histos['GenStoppt'], tr.GenPart_pt[i])

        if abs(tr.GenPart_pdgId[i]) ==5 and tr.GenPart_genPartIdxMother[i] != -1:
                if abs(tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[i]])==1000006 and tr.GenPart_statusFlags[tr.GenPart_genPartIdxMother[i]]!=10497:
                    #print 'particle idx: ', i, 'statusflag: ', tr.GenPart_statusFlags[i], 'status: ', tr.GenPart_status[i], 'mother pdg: ', tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[i]]
                    #if tr.GenPart_statusFlags[i]%2 !=1:       
                    #    for j in range(tr.nGenPart):
                    #        print 'particle idx: ', j, 'pdgID: ',	tr.GenPart_pdgId[j], 'flag: ', tr.GenPart_statusFlags[j], 'status: ', tr.GenPart_status[j], 'mother idx: ', tr.GenPart_genPartIdxMother[j]
                    Fill1D(histos['GenBpt'], tr.GenPart_pt[i])
                     
print 'TreeEntries: ', n_entries
print 'no of events: ', nEvents
print 'Muon integral', histos['GenMuonpt'].Integral()
print 'Stop integral', histos['GenStoppt'].Integral()
print 'LSP integral', histos['GenLSPpt'].Integral()
print 'B integral', histos['GenBpt'].Integral()

c = ROOT.TCanvas('c', '', 600, 800)
c.cd()
histos['GenMustatus'].Draw("histE")
ROOT.gPad.SetLogy()
htitle = histos['GenMustatus'].GetTitle()
c.SaveAs(htitle+".png")
c.Close()
    
    
