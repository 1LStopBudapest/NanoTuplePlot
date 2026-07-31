import ROOT
import math
import os, sys

from Helper.VarCalc import sortedlist, GenFlagString

from ANEle_LL import ANEle

class TmpVar():

    def __init__(self, tr, objtype='comb', pref='Std'):
        self.tr = tr
        self.objtype = objtype #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both satrting from low pT ele
        self.pref = pref # pref is string which defines the preference between standard and low pT ele while using the 'comb' objtype


    def selectEleIdx(self, lepsel):
        return ANEle(self.tr, self.objtype, self.pref).getANEleIdx(lepsel) #return a list of tuple where tuple contain index and collection type
    
 
    def selectMuIdx(self, lepsel):
        idx = []
        for i in range(len(self.tr.Muon_pt)):
            if self.muonSelector(pt=self.tr.Muon_pt[i], eta=self.tr.Muon_eta[i], iso=self.tr.Muon_miniPFRelIso_all[i], dxy=self.tr.Muon_dxy[i], dz=self.tr.Muon_dz[i], Id=self.tr.Muon_looseId[i], lepton_selection=lepsel):
                idx.append(i)
        return idx

    def muonSelector( self, pt, eta, iso, dxy, dz, Id, lepton_selection='HybridIso'):
        if lepton_selection == 'HybridIso':
            def func():
                if pt <= 12 and pt >3:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso* pt) < 2.4 \
                        and Id
                elif pt > 12:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 0.2 \
                        and Id
                
        elif lepton_selection == 'looseHybridIso':
            def func():
                if pt <= 12 and pt >3:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso*pt) < 24.0 \
                        and Id
                elif pt > 12:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 2.0 \
                        and Id
        else:
            def func():
                return \
                    pt >3 \
                    and abs(eta)       < 2.4 \
                    #and Id
        return func()



    def getGenEleIdx(self, momid):
        idx = {}
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) == 11 and self.tr.GenPart_status[i]== 1 and GenFlagString(self.tr.GenPart_statusFlags[i])[1]=='1' and self.hasMomRecursive(i, momid):
                if self.hasMomRecursive(i, 24) and not self.hasMomRecursiveQuark(i):
                    idx[i] = 'EWK'
                elif self.hasMomRecursiveQuark(i):
                    idx[i] = 'quark'
                else:
                    idx[i] = 'radiative&hadrons'

        return idx

    def getGenMuIdx(self, momid):
        idx = {}
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) == 13 and self.tr.GenPart_status[i]== 1 and GenFlagString(self.tr.GenPart_statusFlags[i])[1]=='1' and self.hasMomRecursive(i, momid):
                if self.hasMomRecursive(i, 24) and not self.hasMomRecursiveQuark(i):
                    idx[i] = 'EWK'
                elif self.hasMomRecursiveQuark(i):
                    idx[i] = 'quark'
                else:
                    idx[i] = 'radiative&hadrons'

        return idx
    
    def hasMomRecursive(self, idx, pdgid, max_it=200, current_it=0):
        if current_it >= max_it:
            return False
        if( self.tr.GenPart_genPartIdxMother[idx] < 0 or self.tr.GenPart_genPartIdxMother[idx] >= self.tr.nGenPart):
            return False
        if(abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[idx]]) == pdgid):
            return True
        
        return self.hasMomRecursive(self.tr.GenPart_genPartIdxMother[idx], pdgid, max_it, current_it + 1)

    def getGenEleIdxMomIdx(self, momidx):
        idx = {}
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) == 11 and self.tr.GenPart_status[i]== 1 and GenFlagString(self.tr.GenPart_statusFlags[i])[1]=='1' and self.hasMomRecursiveMomIdx(i, momidx):
                if self.hasMomRecursive(i, 24) and not self.hasMomRecursiveQuark(i):
                    idx[i] = 'EWK'
                elif self.hasMomRecursiveQuark(i):
                    idx[i] = 'quark'
                else:
                    idx[i] = 'radiative&hadrons'

        return idx

    def getGenMuIdxMomIdx(self, momidx):
        idx = {}
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) == 13 and self.tr.GenPart_status[i]== 1 and GenFlagString(self.tr.GenPart_statusFlags[i])[1]=='1' and self.hasMomRecursiveMomIdx(i, momidx):
                if self.hasMomRecursive(i, 24) and not self.hasMomRecursiveQuark(i):
                    idx[i] = 'EWK'
                elif self.hasMomRecursiveQuark(i):
                    idx[i] = 'quark'
                else:
                    idx[i] = 'radiative&hadrons'

        return idx
    
    def hasMomRecursiveMomIdx(self, idx, momidx, max_it=200, current_it=0):
        if current_it >= max_it:
            return False
        if( self.tr.GenPart_genPartIdxMother[idx] < 0 or self.tr.GenPart_genPartIdxMother[idx] >= self.tr.nGenPart):
            return False
        if(self.tr.GenPart_genPartIdxMother[idx] == momidx):
            return True
        
        return self.hasMomRecursiveMomIdx(self.tr.GenPart_genPartIdxMother[idx], momidx, max_it, current_it + 1)
    
    def hasMomRecursiveQuark(self, idx):
        f = False
        for mid in [1, 2, 3, 4, 5]:
            if self.hasMomRecursive(idx, mid):
                f = True
                break
        return f

    def getLSPIdx(self):
        idx = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) ==1000022 and self.tr.GenPart_genPartIdxMother[i] >= 0 and self.tr.GenPart_genPartIdxMother[i]<self.tr.nGenPart:
                if abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[i]])==1000006:
                    idx.append(((i, self.tr.GenPart_genPartIdxMother[i])))
        return idx
