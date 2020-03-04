import ROOT

class VarHandler():
    
    def __init__(self, tr):
        self.tr = tr
        
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

    def cntBtagjet(self, discOpt, thrsld):
        nb = 0
        if discOpt == 'CSVV2':
            disc = self.tr.Jet_btagCSVV2
            thr = 0.8484
        else:
            disc = self.tr.Jet_btagDeepB
            thr = 0.6321
        for i in range(len(self.tr.Jet_pt)):
            if len(self.tr.Jet_pt) and self.tr.Jet_pt[i]>thrsld and abs(self.tr.Jet_eta[i])<2.4:
                if disc[i]>thr:nb=nb+1
        return nb

    def cntMuon(self):
        nm = 0
        for i in range(len(self.tr.Muon_pt)):
            if self.tr.Muon_pt[i]>3.5 and abs(self.tr.Muon_eta[i])<2.4 and self.tr.Muon_isPFcand[i] and (self.tr.Muon_isGlobal[i] or self.tr.Muon_isTracker[i]):
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
