import ROOT
import types
import os, sys

from VarHandler import VarHandler

sys.path.append('../')
from Helper.VarCalc import *
from Helper.TreeVarSel import TreeVarSel
from Helper.MCWeight import MCWeight

class FillHistos():

    def __init__(self, histos, chain, year, nEvents, sample, DataLumi=1.0, NoMCWeight = True):
        self.histos = histos
        self.chain = chain
        self.year = year
        self.nEvents = nEvents
        self.sample = sample
        self.DataLumi = DataLumi
        self.NoCorr = NoMCWeight

        self.isData = True if ('Run' in self.sample or 'Data' in self.sample) else False
        self.isSignal = True if ('Stop' in self.sample or 'T2tt' in self.sample) else False
        
        keylist = ['MET', 'HT', 'Leppt', 'LepMT', 'CT1', 'CT2', 'ISRJetPt', 'Njet20', 'Njet30', 'Nbjet20', 'Nbjet30', 'Nmu', 'Ne', 
                   'Muonpt', 'Muondxy', 'Muondz', 'Elept', 'Eledxy', 'Eledz', '2ndJetPt', '2ndJetEta', 'ISRJetEta', '3rdJetPt', '3rdJetEta',
                   'JetPt', 'JetEta', 'BjetPt', '1stBjetPt', '1stBjetEta', 'DeltaPhi_Jets', 'DeltaPhi_Jets60']
        if not self.isData:
            keylist.extend(['GenMuonpt', 'GenElept', 'GenBpt'])

        if self.isSignal:
            keylist.extend(['GenStoppt', 'GenLSPpt', 'GenBjetpt', 'NGenBjets'])

        self.vardic = {key: None for key in keylist}
    
    def fill(self):
        tr = self.chain
        vardic = self.vardic
        n_entries = tr.GetEntries()
        nevtcut = n_entries -1 if self.nEvents == - 1 else self.nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            tr.GetEntry(ientry)
            if self.isData:
                lumiscale = 1.0
            elif self.isSignal:
                lumiscale = 1.0
            else:
                lumiscale = (self.DataLumi/1000.0) * tr.weight    

            if self.isData or self.isSignal or self.NoCorr:
                MCcorr = 1.0
            else:
                MCcorr = MCWeight(tr, self.year, self.sample).getTotalWeight()
                
            var = {key: None for key in vardic}#reseting the var dictionary for each event
            getsel = TreeVarSel(tr, self.isData, self.year)
            getvar = VarHandler(tr, self.isData, self.year)
            if getsel.passFilters() and getsel.PreSelection():
                var['MET'] = tr.MET_pt
                var['HT'] = getsel.calHT()
                var['Leppt'] = [x['pt'] for x in getsel.getLepVar(getsel.selectMuIdx(), getsel.selectEleIdx())]
                var['LepMT'] = getsel.getLepMT()
                var['CT1'] = getsel.calCT(1)
                var['CT2'] = getsel.calCT(2)
                var['ISRJetPt'] = getsel.getISRPt()
                var['ISRJetEta'] = getsel.getISRJetEta()
                var['2ndJetPt'] = getsel.getNthJetPt(N=2)
                var['2ndJetEta'] = getsel.getNthJetEta(N=2)
                var['3rdJetPt'] = getsel.getNthJetPt(N=3)
                var['3rdJetEta'] = getsel.getNthJetEta(N=3)
                var['JetPt'] = [x for x in getsel.getJetPt()]
                var['JetEta'] = [x for x in getsel.getJetEta()]

                var['DeltaPhi_Jets'] = getvar.getDeltaPhiJets()
                var['DeltaPhi_Jets60'] = getvar.getDeltaPhiJets(secondJetPt=60)
                var['1stBjetPt'] = getvar.get1stBjetPt()
                var['1stBjetEta'] = getvar.get1stBjetEta()

                var['Njet20'] = getvar.calNj(20)
                var['Njet30'] = getvar.calNj(30)
                var['Nbjet20'] = getvar.cntBtagjet('CSVV2', 20)
                var['Nbjet30'] = getvar.cntBtagjet('CSVV2', 30)
                var['BjetPt'] = [x for x in getvar.getBjetPt()]
                var['Nmu'] =     getvar.cntMuon()
                var['Ne'] =     getvar.cntEle()
                var['Muonpt'] = [x for x in getvar.getMuVar()['pt']]
                var['Muondxy'] = [x for x in getvar.getMuVar()['dxy']]
                var['Muondz'] = [x for x in getvar.getMuVar()['dz']]
                var['Elept'] = [x for x in getvar.getEleVar()['pt']]
                var['Eledxy'] = [x for x in getvar.getEleVar()['dxy']]
                var['Eledz'] = [x for x in getvar.getEleVar()['dz']]
                
            if not self.isData:
                var['GenMuonpt'] = [x['pt'] for x in getvar.genMuon()]
                var['GenElept'] = [x['pt'] for x in getvar.genEle()]
                var['GenBpt'] = [x['pt'] for x in getvar.genB()]
            if self.isSignal:
                var['GenStoppt'] = [x['pt'] for x in getvar.genStop()]
                var['GenLSPpt'] = [x['pt'] for x in getvar.genLSP()]                
                var['GenBjetpt'] = [tr.GenJet_pt[x] for x in getvar.selectGenjetIdx()]
                var['NGenBjets'] = len(getvar.selectGenjetIdx())
            
                

                    
            for key in self.histos:
                if key in var.keys():
                    if var[key] is not None:
                        if isinstance(var[key], types.ListType):
                            for x in var[key]: Fill1D(self.histos[key], x, lumiscale * MCcorr)
                        else:
                            Fill1D(self.histos[key], var[key], lumiscale * MCcorr)
                else:
                    #raise ValueError("You are trying to fill the histos for the keys which are missing in var dictionary")
                    print "You are trying to fill the histos for the keys", key, " which are missing in var dictionary"
