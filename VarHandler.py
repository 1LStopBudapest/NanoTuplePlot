import ROOT
import math

from VarCalc import *

class VarHandler():
    
    def __init__(self, tr, yr):
        self.tr = tr
        self.yr = yr

    #cuts
    def ISRcut(self):
        return len(self.selectISRjetIdx())>0

    def METcut(self):
        cut = False
        if self.tr.MET_pt >280:
            cut = True
        return cut
        
    def HTcut(self):
        cut = False
        HT = self.calHT()
        if HT >200:
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
        
    def calHT(self):
        HT = 0
        for i in self.selectjetIdx(30):
            HT = HT + self.tr.Jet_pt[i]
        return HT

    def calNj(self, thrsld):
        return len(self.selectjetIdx(thrsld))
        
    def getISRPt(self):
        return self.tr.Jet_pt[self.selectISRjetIdx()[0]]
    
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
            if self.eleSelector(self.tr.Electron_pt[i], self.tr.Electron_eta[i], self.tr.Electron_pfRelIso03_all[i], self.tr.Electron_cutBased_Fall17_V1, self.tr.Electron_dxy[i], self.tr.Electron_dz[i], 'looseHybridIso'):
                idx.append(i)              
	return idx

    def selectMuIdx(self):
        idx = []
        for i in range(len(self.tr.Muon_pt)):
            if self.muonSelector(self.tr.Muon_pt[i], self.tr.Muon_eta[i], self.tr.Muon_pfRelIso03_all[i], self.tr.Muon_mediumId[i], self.tr.Muon_dxy[i], self.tr.Muon_dz[i], 'looseHybridIso'):
                idx.append(i)
        return idx
    
    def getMuonvar(self):
        muon = {'pt':[], 'dxy':[], 'dz':[]}
        for i in range(len(self.tr.Muon_pt)):
            if self.tr.Muon_pt[i]>3.5 and abs(self.tr.Muon_eta[i])<2.4 and self.tr.Muon_isPFcand[i] and (self.tr.Muon_isGlobal[i] or self.tr.Muon_isTracker[i]):
                muon['pt'].append(self.tr.Muon_pt[i])
                muon['dxy'].append(self.tr.Muon_dxy[i])
                muon['dz'].append(self.tr.Muon_dz[i])

        return muon



    def	getElevar(self):
        ele = {'pt':[], 'dxy':[], 'dz':[]}
        for i in range(len(self.tr.Electron_pt)):
            if self.tr.Electron_pt[i]>5 and abs(self.tr.Electron_eta[i])<2.5 :
                ele['pt'].append(self.tr.Electron_pt[i])
	        ele['dxy'].append(self.tr.Electron_dxy[i])
	        ele['dz'].append(self.tr.Electron_dz[i])
        return ele

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
        

    def muonSelector( self, pt, eta, iso, Id, dxy, dz, lepton_selection='hybridIso', year=2016):
        if lepton_selection == 'hybridIso':
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
        return func


    def eleSelector(self, pt, eta, iso, Id, dxy, dz, lepton_selection='hybridIso', year=2016):
        if lepton_selection == 'hybridIso':
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
                    and self.ID(Id,1)
        return func




    def eleID(idval, idtype):
        return idval==idtype
