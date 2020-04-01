import ROOT
import types
import os, sys

from VarHandler import VarHandler

sys.path.append('../')
from Helper.VarCalc import *

class FillHistos():

    def __init__(self, histos, chain, year, nEvents, sample):
        self.histos = histos
        self.chain = chain
        self.year = year
        self.nEvents = nEvents
        self.sample = sample
        
    def fill(self):
        tr = self.chain
        isData = True if 'Run' in self.sample else False
        isSignal = True if ('Stop' in self.sample or 'T2' in self.sample) else False 
        n_entries = tr.GetEntries()
        for ientry in range(n_entries):
            if not self.nEvents == -1 and ientry > self.nEvents - 1: break
            tr.GetEntry(ientry)
            getvar = VarHandler(tr, self.year)
            cut = getvar.ISRcut() and getvar.METcut() and getvar.HTcut() #and getvar.lepcut() and getvar.dphicut()
            var = {}
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
                
                var['GenMuonpt'] = [x['pt'] for x in getvar.genMuon()] if isSignal else 0
                var['GenElept'] = [x['pt'] for x in getvar.genEle()] if isSignal else 0
                var['GenBpt'] = [x['pt'] for x in getvar.genB()] if isSignal else 0
                var['GenStoppt'] = [x['pt'] for x in getvar.genStop()] if isSignal else 0
                var['GenLSPpt'] = [x['pt'] for x in getvar.genLSP()] if isSignal else 0
                    
                for key in self.histos:
                    try:
                        if isinstance(var[key], types.ListType):
                            for x in var[key]: Fill1D(self.histos[key], x)
                        else:
                            Fill1D(self.histos[key], var[key])
                    except:
                        raise ValueError("You are trying to fill the histos for the keys which are missing in var dictionary")
