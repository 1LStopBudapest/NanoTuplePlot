import ROOT
import math
import os, sys

sys.path.append('../')
from Helper.VarCalc import *

class VarHandler():
    
    def __init__(self, tr, isData, yr):
        self.tr = tr
        self.yr = yr
        self.isData = isData
        
    #cuts
    def ISRcut(self):
        return len(self.selectISRjetIdx())>0

    def METcut(self):
        cut = False
        if self.tr.MET_pt >200:
            cut = True
        return cut
        
    def HTcut(self):
        cut = False
        HT = self.calHT()
        if HT >300:
            cut = True
        return cut

    def dphicut(self):
        cut = False
        if len(self.selectjetIdx(30)) >=2 and self.tr.Jet_pt[self.selectjetIdx(30)[1]]> 60:
            if DeltaPhi(self.tr.Jet_phi[self.selectjetIdx(30)[0]], self.tr.Jet_phi[self.selectjetIdx(30)[1]])<2.5:
                cut = True
        return cut

    def lepcut(self):
        return len(self.getLepVar(self.selectMuIdx(), self.selectEleIdx())) >= 1
    

    def XtralepVeto(self):
        cut = True
        lepvar = sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))
        if len(lepvar) > 1 and lepvar[1]['pt']>20:
            cut = False
        return cut

    def XtraJetVeto(self):
        cut = True
        if len(self.selectjetIdx(30)) >=3 and self.tr.Jet_pt[self.selectjetIdx(30)[2]]> 60:
            cut = False
        return cut

    def tauVeto(self):
        cut = True
        if self.tr.nTau>=1:#only applicable to postprocessed sample where lepton(e,mu)-cleaned (dR<0.4) tau collection is stored
            cut = False
        return cut
            
    def getLepMT(self):
        lepvar = sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))
        return MT(lepvar[0]['pt'], lepvar[0]['phi'], self.tr.MET_pt, self.tr.MET_phi) if len(lepvar) else 0

    def calCT(self, i):
        return CT1(self.tr.MET_pt, self.calHT()) if i==1 else CT2(self.tr.MET_pt, self.getISRPt())
        
    def calHT(self):
        HT = 0
        for i in self.selectjetIdx(30):
            HT = HT + self.tr.Jet_pt[i]
        return HT

    def calNj(self, thrsld):
        return len(self.selectjetIdx(thrsld))
        
    def getISRPt(self):
        return self.tr.Jet_pt[self.selectISRjetIdx()[0]] if len(self.selectISRjetIdx()) else 0
    
    def cntBtagjet(self, discOpt='DeepCSV', ptthrsld=20):
        return len(self.selectBjetIdx(discOpt, ptthrsld))

    def cntMuon(self):
        return len(self.selectMuIdx())

    def	cntEle(self):
    	return len(self.selectEleIdx())
    
    def selectjetIdx(self, thrsld):
        idx = []
        for i in range(len(self.tr.Jet_pt)):
            if self.tr.Jet_pt[i]>thrsld and abs(self.tr.Jet_eta[i])<2.4:
                idx.append(i)
        return idx

    def selectISRjetIdx(self, thrsld=100):
        idx = []
        for i in range(len(self.tr.Jet_pt)):
            if self.tr.Jet_pt[i]>thrsld and abs(self.tr.Jet_eta[i])<2.4:
                idx.append(i)
        return idx

    def selectBjetIdx(self, discOpt='DeepCSV', ptthrsld=20):
        idx = []
        for i in range(len(self.tr.Jet_pt)):
            if self.tr.Jet_pt[i]>ptthrsld and abs(self.tr.Jet_eta[i])<2.4:
                if (self.isBtagCSVv2(self.tr.Jet_btagCSVV2[i], self.yr) if discOpt == 'CSVV2' else self.isBtagDeepCSV(self.tr.Jet_btagDeepB[i], self.yr)):
                    idx.append(i)
        return idx

    def	selectEleIdx(self):
        idx = []
        for i in range(len(self.tr.Electron_pt)):
            if self.eleSelector(pt=self.tr.Electron_pt[i], eta=self.tr.Electron_eta[i], iso=self.tr.Electron_pfRelIso03_all[i], dxy=self.tr.Electron_dxy[i], dz=self.tr.Electron_dz[i], Id=self.tr.Electron_cutBased_Fall17_V1[i],lepton_selection='HybridIso'):
                idx.append(i)              
	return idx

    def selectMuIdx(self):
        idx = []
        for i in range(len(self.tr.Muon_pt)):
            if self.muonSelector(pt=self.tr.Muon_pt[i], eta=self.tr.Muon_eta[i], iso=self.tr.Muon_pfRelIso03_all[i], dxy=self.tr.Muon_dxy[i], dz=self.tr.Muon_dz[i], lepton_selection='HybridIso'):
                idx.append(i)
        return idx
    

    def getLepVar(self, muId, eId):
        Llist = []
        for id in muId:
            Llist.append({'pt':self.tr.Muon_pt[id], 'eta':self.tr.Muon_eta[id], 'phi':self.tr.Muon_phi[id], 'dxy':self.tr.Muon_dxy[id], 'dz': self.tr.Muon_dz[id]})
        for id in eId:
            Llist.append({'pt':self.tr.Electron_pt[id], 'eta':self.tr.Electron_eta[id], 'phi':self.tr.Electron_phi[id], 'dxy':self.tr.Electron_dxy[id], 'dz': self.tr.Electron_dz[id]})
        return Llist

    def isBtagDeepCSV(self, jetb, year):
        if year == 2016:
            return jetb > 0.6321
        elif year == 2017:
            return jetb > 0.4941
        elif year == 2018:
            return jetb > 0.4184
        else:
            return True

    def isBtagCSVv2(self, jetb, year):
        if year == 2016:
            return jetb > 0.8484
        elif year == 2017 or year == 2018:
            return jetb > 0.8838
        else:
            return True
        

    def muonSelector( self, pt, eta, iso, dxy, dz, Id = True, lepton_selection='HybridIso', year=2016):
        if lepton_selection == 'HybridIso':
            def func():
                if pt <= 25 and pt >3.5:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso* pt) < 5.0 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and Id
                elif pt > 25:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 0.2 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and Id
            
        elif lepton_selection == 'looseHybridIso':
            def func():
                if pt <= 25 and pt >3.5:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso*pt) < 20.0 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and Id
                elif pt > 25:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 0.8 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and Id
        else:
            def func():
                return \
                    pt >3.5 \
                    and abs(eta)       < 2.4 \
                    and Id
        return func()


    def eleSelector(self, pt, eta, iso, dxy, dz, Id, lepton_selection='HybridIso', year=2016):
        if lepton_selection == 'HybridIso':
            def func():
                if pt <= 25 and pt >5:
                    return \
                        abs(eta)       < 2.5 \
                        and (iso* pt) < 5.0 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and self.eleID(Id, 1) #cutbased id: 0:fail, 1:veto, 2:loose, 3:medium, 4:tight
                elif pt > 25:
                    return \
                        abs(eta)       < 2.5 \
                        and iso < 0.2 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and self.eleID(Id,1)

        elif lepton_selection == 'looseHybridIso':
            def func():
                if pt <= 25 and pt >5:
                    return \
                        abs(eta)       < 2.5 \
                        and (iso*pt) < 20.0 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and self.eleID(Id,1)
                elif pt > 25:
                    return \
                        abs(eta)       < 2.5 \
                        and iso < 0.8 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and self.eleID(Id,1)

        else:
            def func():
                return \
                    pt >5 \
                    and abs(eta)       < 2.5 \
                    and self.eleID(Id,1)
        return func()




    def eleID(idval, idtype):
        return idval==idtype

    def getMuonvar(self):
        muon = {'pt':[], 'dxy':[], 'dz':[]}
        for i in range(len(self.tr.Muon_pt)):
            if self.tr.Muon_pt[i]>3.5 and abs(self.tr.Muon_eta[i])<2.4 and self.tr.Muon_isPFcand[i] and (self.tr.Muon_isGlobal[i] or self.tr.Muon_isTracker[i]):
                if not self.isData:
                    if DeltaRMatched(self.tr.Muon_eta[i], self.tr.Muon_phi[i], self.genMuon(), 0.3):
                        muon['pt'].append(self.tr.Muon_pt[i])
                        muon['dxy'].append(self.tr.Muon_dxy[i])
                        muon['dz'].append(self.tr.Muon_dz[i])
                else:
                    muon['pt'].append(self.tr.Muon_pt[i])
                    muon['dxy'].append(self.tr.Muon_dxy[i])
                    muon['dz'].append(self.tr.Muon_dz[i])
        return muon



    def	getElevar(self):
        ele = {'pt':[], 'dxy':[], 'dz':[]}
        for i in range(len(self.tr.Electron_pt)):
            if self.tr.Electron_pt[i]>5 and abs(self.tr.Electron_eta[i])<2.5 :
                if not self.isData:
                    if DeltaRMatched(self.tr.Electron_eta[i], self.tr.Electron_phi[i], self.genEle(), 0.3):
                        ele['pt'].append(self.tr.Electron_pt[i])
	                ele['dxy'].append(self.tr.Electron_dxy[i])
	                ele['dz'].append(self.tr.Electron_dz[i])
                else:
                    ele['pt'].append(self.tr.Electron_pt[i])
	            ele['dxy'].append(self.tr.Electron_dxy[i])
                    ele['dz'].append(self.tr.Electron_dz[i])
        return ele
    
    def genEle(self):
        L = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) ==11 and GenFlagString(self.tr.GenPart_statusFlags[i])[-1]=='1' and GenFlagString(self.tr.GenPart_statusFlags[i])[6]=='1' and self.tr.GenPart_status[i]==1 and self.tr.GenPart_genPartIdxMother[i] != -1:
                if abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[i]])!=21:
                    L.append({'pt':self.tr.GenPart_pt[i], 'eta':self.tr.GenPart_eta[i], 'phi':self.tr.GenPart_phi[i]})
        return L

    def genMuon(self):
        L = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) ==13 and GenFlagString(self.tr.GenPart_statusFlags[i])[-1]=='1' and GenFlagString(self.tr.GenPart_statusFlags[i])[6]=='1' and self.tr.GenPart_status[i]==1 and self.tr.GenPart_genPartIdxMother[i] != -1:
                if abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[i]])!=22:
                    L.append({'pt':self.tr.GenPart_pt[i], 'eta':self.tr.GenPart_eta[i], 'phi':self.tr.GenPart_phi[i]})
        return L

    def genB(self):
        L = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) ==5 and self.tr.GenPart_genPartIdxMother[i] != -1 and self.tr.GenPart_genPartIdxMother[i]<self.tr.nGenPart:
                if abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[i]])==1000006 and self.tr.GenPart_statusFlags[self.tr.GenPart_genPartIdxMother[i]]==10497:
                        L.append({'pt':self.tr.GenPart_pt[i], 'eta':self.tr.GenPart_eta[i], 'phi':self.tr.GenPart_phi[i]})
        
        return L

    def genStop(self):
        L = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i])==1000006 and self.tr.GenPart_statusFlags[i]==10497:
                L.append({'pt':self.tr.GenPart_pt[i], 'eta':self.tr.GenPart_eta[i], 'phi':self.tr.GenPart_phi[i]})
        return L

    def genLSP(self):
        L = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) ==1000022 and self.tr.GenPart_genPartIdxMother[i] != -1:
                if abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[i]])==1000006 and self.tr.GenPart_statusFlags[self.tr.GenPart_genPartIdxMother[i]]==10497:
                    L.append({'pt':self.tr.GenPart_pt[i], 'eta':self.tr.GenPart_eta[i], 'phi':self.tr.GenPart_phi[i]})
        return L

    def selectGenjetIdx(self, flavor = 5):
        idx = []
        for i in range(self.tr.nGenJet):
            if abs(self.tr.GenJet_partonFlavour[i])==flavor:
                idx.append(i)
        return idx
