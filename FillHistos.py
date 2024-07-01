import ROOT
import types
import os, sys

from VarHandler import VarHandler

sys.path.append('../')
from Helper.VarCalc import *
from Helper.MCWeight import MCWeight
from Helper.GenFilterEff import GenFilterEff
from Helper.TreeVarSel import TreeVarSel


class FillHistos():

    def __init__(self, histos, chain, year, nEvents, sample, vList, DataLumi=1.0, NoMCWeight = True):
        self.histos = histos
        self.chain = chain
        self.year = year
        self.nEvents = nEvents
        self.sample = sample
        self.DataLumi = DataLumi
        self.vList = vList
        self.NoCorr = NoMCWeight

        self.isData = True if ('Run' in self.sample or 'Data' in self.sample) else False
        self.isSignal = True if ('Stop' in self.sample or 'T2tt' in self.sample) else False
        self.isSignalPoint = True if 'Sig' in self.sample else False

        gfiltr = GenFilterEff(self.year)
        if self.isSignal:
            ms = int(self.sample.split('_')[1])
            ml = int(self.sample.split('_')[2])
            self.gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
        elif self.isSignalPoint:
            ms = int(self.sample.split('_')[2])
            ml = int(self.sample.split('_')[3])
            self.gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
        else:
            self.gfltreff = 1.0         
            
        keylist = self.vList
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
            else:
                lumiscale = (self.DataLumi/1000.0) * tr.weight    

            if self.isData or self.NoCorr:
                MCcorr = 1.0
            else:
                MCcorr = MCWeight(tr, self.year, self.sample).getTotalWeight() *  self.gfltreff
                
            var = {key: None for key in vardic}#reseting the var dictionary for each event
            getsel = TreeVarSel(tr, self.isData, self.year)
            if getsel.passFilters() and getsel.PreSelection():
                var['MET'] = tr.MET_pt
                var['ISRJetPt'] = getsel.getISRPt()
                var['HT'] = getsel.calHT()
                var['LepMT'] = getsel.getLepMT()
                var['CT1'] = getsel.calCT(1)
                var['CT2'] = getsel.calCT(2)
                #var['LeppT'] = [x['pt'] for x in getsel.getSortedLepVar()]
                var['LeppT'] = getsel.getSortedLepVar()[0]['pt']#only the leading lepton
                var['Njet'] = getsel.calNj()
                var['Nbjet'] = getsel.cntBtagjet()
                '''
                var['Muonpt'] = [x for x in getsel.getMuVar()['pt']]
                var['Elept'] = [x for x in getsel.getEleVar()['pt']]
                '''
            '''
            if not self.isData:
                var['GenMuonpt'] = [x['pt'] for x in getsel.genMuon()]
                var['GenElept'] = [x['pt'] for x in getsel.genEle()]
                var['GenBpt'] = [x['pt'] for x in getsel.genB()]
            if self.isSignal or self.isSignalPoint:
                var['GenStoppt'] = [x['pt'] for x in getsel.genStop()]
                var['GenLSPpt'] = [x['pt'] for x in getsel.genLSP()]
            '''
                    
            for key in self.histos:
                if key in var.keys():
                    if var[key] is not None:
                        if isinstance(var[key], types.ListType):
                            for x in var[key]: Fill1D(self.histos[key], x, lumiscale * MCcorr)
                        else:
                            Fill1D(self.histos[key], var[key], lumiscale * MCcorr)
                else:
                    print "You are trying to fill the histos for the keys", key, " which are missing in var dictionary"
