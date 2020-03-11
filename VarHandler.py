import ROOT
import math

class VarHandler():
    
    def __init__(self, tr, yr):
        self.tr = tr
        self.yr = yr

    #cuts
    def ISRcut(self):
        cut = False
        if len(self.tr.Jet_pt) and self.tr.Jet_pt[0]>100 and abs(self.tr.Jet_eta[0])<2.4:
            cut = True
        return cut

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



    def calHT(self):
        HT = 0
        for i in range(len(self.tr.Jet_pt)):
            if self.tr.Jet_pt[i]>30 and abs(self.tr.Jet_eta[i])<2.4:
                HT = HT + self.tr.Jet_pt[i]
        return HT

    def calNj(self, thrsld):
        nj = 0
        for i in range(len(self.tr.Jet_pt)):
            if self.tr.Jet_pt[i]>thrsld and abs(self.tr.Jet_eta[i])<2.4:
                nj = nj+1
        return nj

    def getISRPt(self):
        if len(self.tr.Jet_pt) and self.tr.Jet_pt[0]>100 and abs(self.tr.Jet_eta[0])<2.4:
            return self.tr.Jet_pt[0]
        else:
            return 0

    def cntBtagjet(self, discOpt='DeepCSV', ptthrsld=20):
        nb = 0
        for i in range(len(self.tr.Jet_pt)):
            if self.tr.Jet_pt[i]>ptthrsld and abs(self.tr.Jet_eta[i])<2.4:
                if (self.isBtagCSVv2(self.tr.Jet_btagCSVV2[i], self.yr) if discOpt == 'CSVV2' else self.isBtagDeepCSV(self.tr.Jet_btagDeepB[i], self.yr)):
                    nb=nb+1
        return nb

    def cntMuon(self):
        nm = 0
        for i in range(len(self.tr.Muon_pt)):
            if muonSelector(self.tr.Muon_pt[i], self.tr.Muon_eta[i], self.tr.Muon_looseId[i], self.tr.Muon_dxy[i], self.tr.Muon_dz[i], 'Other'):
                nm = nm+1
        return nm

    def getMuonvar(self):
        muon = {'pt':[], 'dxy':[], 'dz':[]}
        for i in range(len(self.tr.Muon_pt)):
            if self.tr.Muon_pt[i]>3.5 and abs(self.tr.Muon_eta[i])<2.4 and self.tr.Muon_isPFcand[i] and (self.tr.Muon_isGlobal[i] or self.tr.Muon_isTracker[i]):
                muon['pt'].append(self.tr.Muon_pt[i])
                muon['dxy'].append(self.tr.Muon_dxy[i])
                muon['dz'].append(self.tr.Muon_dz[i])

        return muon

    def	cntEle(self):
        ne = 0
        for i in range(len(self.tr.Electron_pt)):
            if self.tr.Electron_pt[i]>5 and abs(self.tr.Electron_eta[i])<2.5 :
                ne = ne+1
	return ne

    def	getElevar(self):
        ele = {'pt':[], 'dxy':[], 'dz':[]}
        for i in range(len(self.tr.Electron_pt)):
            if self.tr.Electron_pt[i]>5 and abs(self.tr.Electron_eta[i])<2.5 :
                ele['pt'].append(self.tr.Electron_pt[i])
	        ele['dxy'].append(self.tr.Electron_dxy[i])
	        ele['dz'].append(self.tr.Electron_dz[i])
        return ele


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
                    and abs(eta)       < 2.4
            
        return func
