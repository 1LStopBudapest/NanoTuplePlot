import ROOT
import types

from VarHandler import VarHandler
from VarCalc import *

class FillHistos():

    def __init__(self, histos, chain, year):
        self.histos = histos
        self.chain = chain
        self.year = year
        
    def fill(self):
        tr = self.chain
        n_entries = tr.GetEntries()
        for ientry in range(n_entries):
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
                
                for key in self.histos:
                    try:
                        if isinstance(var[key], types.ListType):
                            for x in var[key]: Fill1D(self.histos[key], x)
                        else:
                            Fill1D(self.histos[key], var[key])
                    except:
                        raise ValueError("You are trying to fill the histos for the keys which are missing in var dictionary")
