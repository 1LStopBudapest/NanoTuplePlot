import ROOT
import types
import os, sys

from VarHandler import VarHandler

sys.path.append('../')
from Helper.VarCalc import *

class FillHistos():

    def __init__(self, histos, chain, year, nEvents, sample, DataLumi=1.0):
        self.histos = histos
        self.chain = chain
        self.year = year
        self.nEvents = nEvents
        self.sample = sample
        self.DataLumi = DataLumi

        self.isData = True if ('Run' in self.sample or 'Data' in self.sample) else False
        self.isSignal = True if ('Stop' in self.sample or 'T2tt' in self.sample) else False
        
        keylist = ['MET', 'HT', 'Njet20', 'Njet30', 'ISRJetPt', 'Nbjet20', 'Nbjet30', 'Nmu', 'Ne', 'Muonpt', 'Muondxy', 'Muondz', 'Elept', 'Eledxy', 'Eledz', 'LepMT', 'CT1', 'CT2']
        if not self.isData:
            keylist.extend(['GenMuonpt', 'GenElept', 'GenBpt'])

        if self.isSignal:
            keylist.extend(['GenStoppt', 'GenLSPpt', 'GenBjetpt', 'NGenBjets'])

        self.var = {key: None for key in keylist}
    
    def fill(self):
        tr = self.chain
        var = self.var
        n_entries = tr.GetEntries()
        nevtcut = n_entries -1 if self.nEvents == - 1 else self.nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            tr.GetEntry(ientry)
            if self.isData:
                lumiscale = 1.0
            else:
                lumiscale = (self.DataLumi/1000.0) * tr.weight    
            getvar = VarHandler(tr, self.isData, self.year)
            cut = getvar.ISRcut() and getvar.METcut() and getvar.HTcut() and getvar.lepcut() and getvar.dphicut() and getvar.XtralepVeto() and getvar.XtraJetVeto() and getvar.tauVeto() #signal region cut
            if cut:
                var['MET'] = tr.MET_pt
                var['HT'] = getvar.calHT()
                var['Njet20'] = getvar.calNj(20)
                var['Njet30'] = getvar.calNj(30)
                var['ISRJetPt'] = getvar.getISRPt()
                var['Nbjet20'] = getvar.cntBtagjet('CSVV2', 20)
                var['Nbjet30'] = getvar.cntBtagjet('CSVV2', 30)
                var['Nmu'] =     getvar.cntMuon()
                var['Ne'] =     getvar.cntEle()
                var['Muonpt'] = [x for x in getvar.getMuonvar()['pt']]
                var['Muondxy'] = [x for x in getvar.getMuonvar()['dxy']]
                var['Muondz'] = [x for x in getvar.getMuonvar()['dz']]
                var['Elept'] = [x for x in getvar.getElevar()['pt']]
                var['Eledxy'] = [x for x in getvar.getElevar()['dxy']]
                var['Eledz'] = [x for x in getvar.getElevar()['dz']]
                var['LepMT'] = getvar.getLepMT()
                var['CT1'] = getvar.calCT(1)
                var['CT2'] = getvar.calCT(2)
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
                            for x in var[key]: Fill1D(self.histos[key], x, lumiscale)
                        else:
                            Fill1D(self.histos[key], var[key], lumiscale)
                else:
                    #raise ValueError("You are trying to fill the histos for the keys which are missing in var dictionary")
                    print "You are trying to fill the histos for the keys", key, " which are missing in var dictionary"
