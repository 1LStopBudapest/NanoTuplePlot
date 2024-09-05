import ROOT
import types
import os, sys

from VarHandler import VarHandler

sys.path.append('../')
from Helper.VarCalc import *
from Helper.MCWeight import MCWeight
from Helper.GenFilterEff import GenFilterEff
from Helper.TreeVarSel_LL import TreeVarSel

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
            if getsel.passFilters() and getsel.PreSelection() and getsel.Dxy2():
                var['MET'] = tr.MET_pt
                var['ISRJetPt'] = getsel.getISRPt()
                var['HT'] = getsel.calHT()
                var['LepMT'] = getsel.getLepMT()
                var['CT1'] = getsel.calCT(1)
                var['CT2'] = getsel.calCT(2)
                var['LeppT'] = getsel.getSortedLepVar()[0]['pt']
                var['Lepdxy'] = abs(getsel.getSortedLepVar()[0]['dxy'])
                var['LepdxySig'] = abs(getsel.getSortedLepVar()[0]['dxy']/getsel.getSortedLepVar()[0]['dxyErr'])
                var['Lepdz'] = abs(getsel.getSortedLepVar()[0]['dz'])
                var['Njet'] = getsel.calNj()
                var['Nbjet'] = getsel.cntBtagjet()
                if getsel.getSortedLepVar()[0]['type'] == 'mu':
                    var['MupT'] = getsel.getSortedLepVar()[0]['pt']
                    var['Mudxy'] = var['Lepdxy'] = abs(getsel.getSortedLepVar()[0]['dxy'])
                    var['Mudz'] = abs(getsel.getSortedLepVar()[0]['dz'])
                else:
                    var['epT'] = getsel.getSortedLepVar()[0]['pt']
                    var['edxy'] = var['Lepdxy'] = abs(getsel.getSortedLepVar()[0]['dxy'])
                    var['edz'] = abs(getsel.getSortedLepVar()[0]['dz'])
                '''
                var['MupT'] = getsel.getMuVar(getsel.selectMuIdx())[0]['pt'] #[x['pt'] for x in getsel.getMuVar(getsel.selectMuIdx())]
                var['Mudxy'] = abs(getsel.getMuVar(getsel.selectMuIdx())[0]['dxy']) #[abs(x['dxy']) for x in getsel.getMuVar(getsel.selectMuIdx())]
                var['Mudz'] = abs(getsel.getMuVar(getsel.selectMuIdx())[0]['dz']) #[abs(x['dz']) for x in getsel.getMuVar(getsel.selectMuIdx())]
                var['epT'] = getsel.getEleVar()[0]['pt'] #[x['pt'] for x in getsel.getEleVar()]
                var['edxy'] = abs(getsel.getEleVar()[0]['dxy']) #[abs(x['dxy']) for x in getsel.getEleVar()]
                var['edz'] = abs(getsel.getEleVar()[0]['dz']) #[abs(x['dz']) for x in getsel.getEleVar()]
                '''
                var['AllLeppT'] = [x['pt'] for x in getsel.getSortedLepVar()]
                var['AllLepdxy'] = [abs(x['dxy']) for x in getsel.getSortedLepVar()]
                var['AllLepdxySig'] = [abs(x['dxy']/x['dxyErr']) for x in getsel.getSortedLepVar()]
                var['AllLepdz'] = [abs(x['dz']) for x in getsel.getSortedLepVar()]
                var['Nlep'] = len(getsel.getSortedLepVar())
                if len(getsel.getSortedLepVar()) > 1:
                    var['2ndLeppT'] = getsel.getSortedLepVar()[1]['pt'] #if len(getsel.getSortedLepVar()) > 1 else -999
                    var['2ndLepeta'] = abs(getsel.getSortedLepVar()[1]['eta']) #if len(getsel.getSortedLepVar()) > 1 else -999
                    var['2ndLepdxy'] = abs(getsel.getSortedLepVar()[1]['dxy']) #if len(getsel.getSortedLepVar()) > 1 else -999
                    var['2ndLepdz'] = abs(getsel.getSortedLepVar()[1]['dz']) #if len(getsel.getSortedLepVar()) > 1 else -999
                
                '''
                if not self.isData:
                    var['GenMuonpt'] = [x['pt'] for x in getvar.genMuon()]
                    var['GenElept'] = [x['pt'] for x in getvar.genEle()]
                    var['GenBpt'] = [x['pt'] for x in getvar.genB()]
                if self.isSignal or self.isSignalPoint:
                    var['GenStoppt'] = [x['pt'] for x in getvar.genStop()]
                    var['GenLSPpt'] = [x['pt'] for x in getvar.genLSP()]
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
