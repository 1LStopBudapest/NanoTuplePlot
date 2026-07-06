import ROOT
import types
import os, sys
import math


sys.path.append('../../')
sys.path.append('../')
from VarHandler import VarHandler
from Helper.VarCalc import *
from Helper.MCWeight import MCWeight
from Helper.GenFilterEff import GenFilterEff
from Helper.TreeVarSel_LL import TreeVarSel
#from Helper.TreeVarSel import TreeVarSel

class FillHistosBothBR():

    def __init__(self, hfile, histos, chain03, chain10, year, nEvents, sample, vList, branching_ratio, DataLumi=1.0, NoMCWeight = True):
        self.histos = histos
        self.chain03 = chain03
        self.chain10 = chain10
        self.year = year
        self.nEvents = nEvents
        self.sample = sample
        self.DataLumi = DataLumi
        self.vList = vList
        self.NoCorr = NoMCWeight
        self.branching_ratio = branching_ratio
        self.hfile = hfile

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
            #print("################################################")
            #print("MS = " +str(ms))
            #print("ML = " +str(ml))
            #print("###################################################")
            self.gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
        else:
            self.gfltreff = 1.0         
            
        keylist = self.vList
        self.vardic = {key: None for key in keylist}

        self.branching_ratio_index = (int) (branching_ratio*10-1)

    def fill2(self):

        #histos03 = self.histos.copy()
        #histos10 = self.histos.copy()

        histos03 = {}
        histos10 = {}

        for name, h in self.histos.items():
            histos03[name] = h.Clone()
            #histos03[name].Reset()

            histos10[name] = h.Clone()
            #histos10[name].Reset()

        print("hist1 pointer:", histos03)
        print("hist2 pointer:", histos10)

        #########################
        #Fill tree with chain from BR 03
        ##########################
        tree03 = self.chain03

        vardic = self.vardic
        n_entries03 = tree03.GetEntries()
        nevtcut03 = n_entries03 -1 if self.nEvents == - 1 else self.nEvents - 1
        print 'Running over total events: ', nevtcut03+1

        selected_events03 = 0
        selected_events10 = 0

        n_rejected_03 = 0
        n_rejected_10 = 0

        for ientry03 in range(n_entries03):

            if ientry03 > nevtcut03: break
            if ientry03 % (nevtcut03/10)==0 : print 'processing ', ientry03,'th event'

            tree03.GetEntry(ientry03)
            if self.isData:
                lumiscale = 1.0
                #####print("Considered as data")
            else:
                lumiscale = (self.DataLumi) * (tree03.weight)/1000.0
                ####print("Considered as mc") 

            if self.isData or self.NoCorr:
                MCcorr = 1.0
            else:
                #MCcorr = MCWeight(tree03, self.year, self.sample).getTotalWeight() *  self.gfltreff
                MCcorr = MCWeight(tree03, self.year, self.sample).getTotalWeight() /  self.gfltreff
            # print("..........MCcorr...................")
            # print(MCcorr)
            # print(".................................")

            #################################################
            ###TEST
            # if weight_BRctau_list[self.branching_ratio_index]>100:
            #     print("ultra long event")
            #     continue
            

            ################################################
                
            var03= {key: None for key in vardic}#reseting the var03dictionary for each event
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel03 = TreeVarSel(tree03, self.isData, self.year, 'comb')
            #if getsel03.passFilters() and getsel03.PreSelection() and getsel03.Dxy2():
            #if getsel03.passFilters() and getsel03.PreSelection():
            if getsel03.passFilters() and getsel03.PreSelection() and getsel03.gen4Body():

                selected_events03 = selected_events03+1

                ###DEBUG MOISES
                if ientry03 % (nevtcut03/10)==0 : 
                    print("MET BR 03 = "+str(tree03.MET_pt))
                
                ####print("lumiscale * MCcorr "+str(lumiscale * MCcorr))

                weight_BRctau_list = tree03.ReweightBRctau
                w_BRctau = weight_BRctau_list[self.branching_ratio_index]
                #w_BRctau = 1
                # print("weight_BRctau_list = "+str(weight_BRctau_list))
                # print("w_BRctau = "+str(w_BRctau))
                
                #############
                var03['stopCtau'] = tree03.stopCtau

                var03['MET'] = tree03.MET_pt
                var03['ISRJetPt'] = getsel03.getISRPt()
                var03['HT'] = getsel03.calHT()
                var03['LepMT'] = getsel03.getLepMT()
                var03['CT1'] = getsel03.calCT(1)
                var03['CT2'] = getsel03.calCT(2)
                
                var03['Lepdxy'] = abs(getsel03.getSortedLepVar()[0]['dxy'])
                var03['LepdxySig'] = ( abs(getsel03.getSortedLepVar()[0]['dxy']/getsel03.getSortedLepVar()[0]['dxyErr']) )
                var03['Lepdz'] = abs(getsel03.getSortedLepVar()[0]['dz'])
                var03['Njet'] = getsel03.calNj()
                var03['Nbjet'] = getsel03.cntBtagjet()

                var03['LeppT'] = getsel03.getSortedLepVar()[0]['pt']
                if getsel03.getSortedLepVar()[0]['type'] == 'mu':
                    var03['MupT'] = getsel03.getSortedLepVar()[0]['pt']
                    var03['Mudxy'] = var03['Lepdxy'] = abs(getsel03.getSortedLepVar()[0]['dxy'])
                    var03['Mudz'] = abs(getsel03.getSortedLepVar()[0]['dz'])
                else:
                    var03['epT'] = getsel03.getSortedLepVar()[0]['pt']
                    var03['edxy'] = var03['Lepdxy'] = abs(getsel03.getSortedLepVar()[0]['dxy'])
                    var03['edz'] = abs(getsel03.getSortedLepVar()[0]['dz'])
                '''
                var03['MupT'] = getsel03.getMuVar(getsel03.selectMuIdx())[0]['pt'] #[x['pt'] for x in getsel03.getMuVar(getsel03.selectMuIdx())]
                var03['Mudxy'] = abs(getsel03.getMuVar(getsel03.selectMuIdx())[0]['dxy']) #[abs(x['dxy']) for x in getsel03.getMuVar(getsel03.selectMuIdx())]
                var03['Mudz'] = abs(getsel03.getMuVar(getsel03.selectMuIdx())[0]['dz']) #[abs(x['dz']) for x in getsel03.getMuVar(getsel03.selectMuIdx())]
                var03['epT'] = getsel03.getEleVar()[0]['pt'] #[x['pt'] for x in getsel03.getEleVar()]
                var03['edxy'] = abs(getsel03.getEleVar()[0]['dxy']) #[abs(x['dxy']) for x in getsel03.getEleVar()]
                var03['edz'] = abs(getsel03.getEleVar()[0]['dz']) #[abs(x['dz']) for x in getsel03.getEleVar()]
                '''
                var03['AllLeppT'] = [x['pt'] for x in getsel03.getSortedLepVar()] 
                var03['AllLepdxy'] = [abs(x['dxy']) for x in getsel03.getSortedLepVar()] 
                var03['AllLepdxySig'] = [abs(x['dxy']/x['dxyErr']) for x in getsel03.getSortedLepVar()] 
                var03['AllLepdz'] = [abs(x['dz']) for x in getsel03.getSortedLepVar()] 
                var03['Nlep'] = len(getsel03.getSortedLepVar())
                if len(getsel03.getSortedLepVar()) > 1:
                    var03['2ndLeppT'] = getsel03.getSortedLepVar()[1]['pt'] #if len(getsel03.getSortedLepVar()) > 1 else -999
                    var03['2ndLepeta'] = abs(getsel03.getSortedLepVar()[1]['eta'])  #if len(getsel03.getSortedLepVar()) > 1 else -999
                    var03['2ndLepdxy'] = abs(getsel03.getSortedLepVar()[1]['dxy']) #if len(getsel03.getSortedLepVar()) > 1 else -999
                    var03['2ndLepdz'] = abs(getsel03.getSortedLepVar()[1]['dz'])  #if len(getsel03.getSortedLepVar()) > 1 else -999

                #print(var03)
                # print("...........................................")
                # print("self.DataLumi = "+str(self.DataLumi))
                # print("lumi weight = "+str((tree03.weight)/1000.0))
                # print("self.gfltreff = "+str(self.gfltreff))
                # print("MCWeight = "+str( MCWeight(tree03, self.year, self.sample).getTotalWeight() ))
                
                for key in histos03:
                    if key in var03.keys():
                        #print("var03[key] is "+str(var03[key])+"  and key is "+str(key))
                        #print("var03[key] is a list "+str(isinstance(var03[key], types.ListType)))
                        if var03[key] is not None:
                            
                            if isinstance(var03[key], types.ListType):
                                 #print("EXEC::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                                for x in var03[key]: Fill1D(histos03[key], x, lumiscale * MCcorr * w_BRctau)
                            else:
                                #print("EXEC2::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                                Fill1D(histos03[key], var03[key], lumiscale * MCcorr * w_BRctau)
                        # else:
                        #     print("var03[key] is "+str(var03[key])+"  and key is "+str(key))
                    else:
                        print "You are trying to fill the histos for the keys", key, " which are missing in var03dictionary"
            else:
                n_rejected_03 +=1
        print("filled BR 0.3......")
        print("Entries in 0.3 histo  "+str('LeppT')+"= "+str(histos03['LeppT'].GetEntries()))
        #########################
        #Fill tree with chain from BR 10
        ##########################
        tree10 = self.chain10

        vardic = self.vardic
        n_entries10 = tree10.GetEntries()
        nevtcut10 = n_entries10 -1 if self.nEvents == - 1 else self.nEvents - 1
        print 'Running over total events: ', nevtcut10+1

        for ientry10 in range(n_entries10):

            if ientry10 > nevtcut10: break
            if ientry10 % (nevtcut10/10)==0 : print 'processing ', ientry10,'th event'

            tree10.GetEntry(ientry10)
            if self.isData:
                lumiscale = 1.0
                #####print("Considered as data")
            else:
                lumiscale = (self.DataLumi) * (tree10.weight)/1000.0
                ####print("Considered as mc") 

            if self.isData or self.NoCorr:
                MCcorr = 1.0
            else:
                #MCcorr = MCWeight(tree10, self.year, self.sample).getTotalWeight() *  self.gfltreff
                MCcorr = MCWeight(tree10, self.year, self.sample).getTotalWeight() /  self.gfltreff

            
                
            var10= {key: None for key in vardic}#reseting the var10dictionary for each event
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel10 = TreeVarSel(tree10, self.isData, self.year, 'comb')
            #if getsel10.passFilters() and getsel10.PreSelection() and getsel10.Dxy2():
            #if getsel10.passFilters() and getsel10.PreSelection():
            if getsel10.passFilters() and getsel10.PreSelection() and getsel10.gen4Body():

                selected_events10 = selected_events10+1

                ###DEBUG MOISES
                if ientry10 % (nevtcut10/10)==0 : 
                    print("MET BR 03 = "+str(tree10.MET_pt))
                    
                ####print("lumiscale * MCcorr "+str(lumiscale * MCcorr))

                weight_BRctau_list = tree10.ReweightBRctau
                w_BRctau = weight_BRctau_list[self.branching_ratio_index]
                #w_BRctau = 1
                # print("weight_BRctau_list = "+str(weight_BRctau_list))
                # print("w_BRctau = "+str(w_BRctau))
                
                #############
                var10['stopCtau'] = tree10.stopCtau 
                
                var10['MET'] = tree10.MET_pt
                var10['ISRJetPt'] = getsel10.getISRPt()
                var10['HT'] = getsel10.calHT() 
                var10['LepMT'] = getsel10.getLepMT() 
                var10['CT1'] = getsel10.calCT(1)
                var10['CT2'] = getsel10.calCT(2)
                
                var10['Lepdxy'] = abs(getsel10.getSortedLepVar()[0]['dxy'])
                var10['LepdxySig'] = ( abs(getsel10.getSortedLepVar()[0]['dxy']/getsel10.getSortedLepVar()[0]['dxyErr']) )
                var10['Lepdz'] = abs(getsel10.getSortedLepVar()[0]['dz'])
                var10['Njet'] = getsel10.calNj()
                var10['Nbjet'] = getsel10.cntBtagjet()

                var10['LeppT'] = getsel10.getSortedLepVar()[0]['pt']
                if getsel10.getSortedLepVar()[0]['type'] == 'mu':
                    var10['MupT'] = getsel10.getSortedLepVar()[0]['pt']
                    var10['Mudxy'] = var10['Lepdxy'] = abs(getsel10.getSortedLepVar()[0]['dxy'])
                    var10['Mudz'] = abs(getsel10.getSortedLepVar()[0]['dz'])
                else:
                    var10['epT'] = getsel10.getSortedLepVar()[0]['pt']
                    var10['edxy'] = var10['Lepdxy'] = abs(getsel10.getSortedLepVar()[0]['dxy'])
                    var10['edz'] = abs(getsel10.getSortedLepVar()[0]['dz'])
                '''
                var10['MupT'] = getsel10.getMuVar(getsel10.selectMuIdx())[0]['pt'] #[x['pt'] for x in getsel10.getMuVar(getsel10.selectMuIdx())]
                var10['Mudxy'] = abs(getsel10.getMuVar(getsel10.selectMuIdx())[0]['dxy']) #[abs(x['dxy']) for x in getsel10.getMuVar(getsel10.selectMuIdx())]
                var10['Mudz'] = abs(getsel10.getMuVar(getsel10.selectMuIdx())[0]['dz']) #[abs(x['dz']) for x in getsel10.getMuVar(getsel10.selectMuIdx())]
                var10['epT'] = getsel10.getEleVar()[0]['pt'] #[x['pt'] for x in getsel10.getEleVar()]
                var10['edxy'] = abs(getsel10.getEleVar()[0]['dxy']) #[abs(x['dxy']) for x in getsel10.getEleVar()]
                var10['edz'] = abs(getsel10.getEleVar()[0]['dz']) #[abs(x['dz']) for x in getsel10.getEleVar()]
                '''
                var10['AllLeppT'] = [x['pt'] for x in getsel10.getSortedLepVar()] 
                var10['AllLepdxy'] = [abs(x['dxy']) for x in getsel10.getSortedLepVar()] 
                var10['AllLepdxySig'] = [abs(x['dxy']/x['dxyErr'])for x in getsel10.getSortedLepVar()] 
                var10['AllLepdz'] = [abs(x['dz'])for x in getsel10.getSortedLepVar()] 
                var10['Nlep'] = len(getsel10.getSortedLepVar())
                if len(getsel10.getSortedLepVar()) > 1:
                    var10['2ndLeppT'] = getsel10.getSortedLepVar()[1]['pt'] #if len(getsel10.getSortedLepVar()) > 1 else -999
                    var10['2ndLepeta'] = abs(getsel10.getSortedLepVar()[1]['eta']) #if len(getsel10.getSortedLepVar()) > 1 else -999
                    var10['2ndLepdxy'] = abs(getsel10.getSortedLepVar()[1]['dxy']) #if len(getsel10.getSortedLepVar()) > 1 else -999
                    var10['2ndLepdz'] = abs(getsel10.getSortedLepVar()[1]['dz']) #if len(getsel10.getSortedLepVar()) > 1 else -999
                
                for key in histos10:
                    if key in var10.keys():
                        if var10[key] is not None:
                            if isinstance(var10[key], types.ListType):
                                for x in var10[key]: Fill1D(histos10[key], x, lumiscale * MCcorr*w_BRctau)
                            else:
                                Fill1D(histos10[key], var10[key], lumiscale * MCcorr*w_BRctau)
                        # else:
                        #     print("var10[key] is "+str(var10[key])+"  and key is "+str(key))
                    else:
                        print "You are trying to fill the histos for the keys", key, " which are missing in var10dictionary"
            else:
                n_rejected_10 +=1
        print("filled BR 1.0......")

        print("Selected Entries in 0.3 histo "+str(selected_events03))
        print("Selected Entries in 1.0 histo "+str(selected_events10))
        print("rejected Entries in 0.3 histo "+str(n_rejected_03))
        print("rejected Entries in 1.0 histo "+str(n_rejected_10))
        print("Entries in 0.3 histo  "+str('LeppT')+"= "+str(histos03['LeppT'].GetEntries()))
        print("Entries in 1.0 histo  "+str('LeppT')+"= "+str(histos10['LeppT'].GetEntries()))

        ##Histogram combination of the two BR
        for key_ in self.histos:
            self.histos[key_] = self.branching_ratio*histos10[key_] + (1-self.branching_ratio)*histos03[key_]
            self.histos[key_].SetDirectory(self.hfile)

            # Now set the errors manually using error propagation
            for i in range(1, self.histos[key_].GetNbinsX() + 1):  # Loop through all bins (1 to NbinsX)
                error10 = histos10[key_].GetBinError(i)
                error03 = histos03[key_].GetBinError(i)
                
                # Calculate the propagated error: sqrt(error1^2 + error2^2)
                propagated_error = math.sqrt((self.branching_ratio**2)*(error10**2) + ((1-self.branching_ratio)**2)*(error03**2))
                
                # Set the error for this bin in the sum histogram
                self.histos[key_].SetBinError(i, propagated_error)
                #self.histos[key_].SetBinError(i, 10)
            print("Entries in 0.3 histo "+str(key_)+"= "+str(histos03[key_].GetEntries()))
            print("Entries in 1.0 histo "+str(key_)+"= "+str(histos10[key_].GetEntries()))
            print("Entries in combined histo = "+str(self.histos[key_].GetEntries()))
            print("Integral in 0.3 histo = "+str(histos03[key_].Integral()))
            print("Integral in 1.0 histo = "+str(histos10[key_].Integral()))
            print("Integral in combined histo = "+str(self.histos[key_].Integral()))
            print("......................")

        print("Combined histograms of the two BR......")
        
        print("wwwwwwwwwwwwwwwwwwwwwwwwww")
        """ print(self.histos)
        for keyes in self.histos:
            print(keyes)
            print(self.histos[keyes].Print("all"))

            # Check if the histogram is valid
            if self.histos[keyes].GetEntries() == 0:
                print("Error: Histogram is empty.") """


        print("wwwwwwwwwwwwwwwwwwwwwwwwww")