import ROOT
import types
import os, sys

from VarHandler import VarHandler

sys.path.append('../')
from Helper.VarCalc import *
from Helper.TreeVarSel import TreeVarSel
from Helper.MCWeight import MCWeight
from Helper.IVFhelper import IVFhelper

class FillHistos_IVF():

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
                   'Muonpt', 'Muondxy', 'Muondz', 'Elept', 'Eledxy', 'Eledz', 'nSV', 'Ntracks', 'SVdxy', 'SVdxySig', 'SVmass', 'SVdlenSig',
                   'SVpAngle', 'SVpT', 'SVdR']
      
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
            lumiscale = 1.0

            if self.isData or self.isSignal or self.NoCorr:
                MCcorr = 1.0
            else:
                MCcorr = MCWeight(tr, self.year, self.sample).getTotalWeight()
                
            var = {key: None for key in vardic}
            getivf = IVFhelper(tr, self.isData, self.year)
            var['nSV'] = tr.nSV
            var['Ntracks'] = [x for x in getivf.getNtracks()]
            var['SVdxy'] = [x for x in getivf.getSVdxy()]
            var['SVdxySig'] = [x for x in getivf.getS2D()]
            var['SVmass'] = [x for x in getivf.getSVmass()]
            var['SVdlenSig'] = [x for x in getivf.getS3D()]
            var['SVpAngle'] = [x for x in getivf.getSVangle()]
            var['SVpT'] = [x for x in getivf.getSVpT()]
            var['SVdR'] = [x for x in getivf.getSVdR()]
               

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
