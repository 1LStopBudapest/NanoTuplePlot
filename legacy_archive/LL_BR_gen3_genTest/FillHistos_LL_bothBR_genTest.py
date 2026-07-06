import ROOT
import types
import os, sys
import math

from VarHandler import VarHandler

sys.path.append('../')
from Helper.VarCalc import *
from Helper.MCWeight import MCWeight
from Helper.GenFilterEff import GenFilterEff
from Helper.TreeVarSel_LL import TreeVarSel
#from Helper.TreeVarSel import TreeVarSel

import csv
def append_row_to_csv(filename, row_data):
    """Append a list as a new row to a CSV file."""
    with open(filename, 'ab') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row_data)

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
            self.ms = ms
            self.ml = ml
        elif self.isSignalPoint:
            ms = int(self.sample.split('_')[2])
            ml = int(self.sample.split('_')[3])
            self.ms = ms
            self.ml = ml
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
        #################################################
        #print("hist1 pointer:", histos03)
        #print("hist2 pointer:", histos10)
        #################################################

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

            #################################################
            ###TEST
            #if ientry03 > 1: break
            ################################################

            if ientry03 > nevtcut03: break
            if ientry03 % (nevtcut03/10)==0 : print 'processing ', ientry03,'th event'

            tree03.GetEntry(ientry03)
            if self.isData:
                lumiscale = 1.0
                #####print("Considered as data")
            else:
                lumiscale = (self.DataLumi) * (tree03.lumi_weight)/1000.0
                ####print("Considered as mc") 

            if self.isData or self.NoCorr:
                MCcorr = 1.0
            else:
                #MCcorr = MCWeight(tree03, self.year, self.sample).getTotalWeight() *  self.gfltreff
                #MCcorr = MCWeight(tree03, self.year, self.sample).getTotalWeight() /  self.gfltreff
                MCcorr = MCWeight(tree03, self.year, self.sample).getTotalWeight()
            # print("..........MCcorr...................")
            # print(MCcorr)
            # print(".................................")

            
                
            var03= {key: None for key in vardic}#reseting the var03dictionary for each event
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel03 = TreeVarSel(tree03, self.isData, self.year, 'comb')
            #if getsel03.passFilters() and getsel03.PreSelection() and getsel03.Dxy2():
            #if getsel03.passFilters() and getsel03.PreSelection():
            #if getsel03.gen4Body():
            if getsel03.gen4Body():

                selected_events03 = selected_events03+1

                weight_BRctau_list = tree03.ReweightBRctau
                w_BRctau = weight_BRctau_list[self.branching_ratio_index]

                #################################################
                ###TEST
                if w_BRctau>100:
                    #print("ultra long event")
                    n_rejected_03 +=1
                    continue
                ################################################
                
                #############
                var03['stopCtau'] = tree03.stopCtau
                var03['MET'] = tree03.MET_pt
                # var03['MCWeight'] = MCWeight(tree03, self.year, self.sample).getTotalWeight()
                # var03['gfltreff'] = self.gfltreff
                # var03['lumiWeight'] = (tree03.lumi_weight)/1000.0
                # var03['w_BRctau'] = w_BRctau
                
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
        print("Entries in 0.3 histo  "+str('MET')+"= "+str(histos03['MET'].GetEntries()))

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
                lumiscale = (self.DataLumi) * (tree10.lumi_weight)/1000.0

            if self.isData or self.NoCorr:
                MCcorr = 1.0
            else:
                #MCcorr = MCWeight(tree10, self.year, self.sample).getTotalWeight() *  self.gfltreff
                #MCcorr = MCWeight(tree10, self.year, self.sample).getTotalWeight() /  self.gfltreff
                #TEST#DELETE WHEN DONE
                MCcorr = MCWeight(tree10, self.year, self.sample).getTotalWeight()
                
            var10= {key: None for key in vardic}#reseting the var10dictionary for each event
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel10 = TreeVarSel(tree10, self.isData, self.year, 'comb')
            #if getsel10.passFilters() and getsel10.PreSelection() and getsel10.Dxy2():
            #if getsel10.passFilters() and getsel10.PreSelection():
            #if getsel10.gen4Body():
            if getsel10.gen4Body():
            
                selected_events10 = selected_events10+1
                
                weight_BRctau_list = tree10.ReweightBRctau
                w_BRctau = weight_BRctau_list[self.branching_ratio_index]

                #################################################
                ###TEST
                if w_BRctau>100:
                    #print("ultra long event")
                    n_rejected_10 +=1
                    continue
                ################################################
                # print("............................")
                # print("w_BRctau = "+str(w_BRctau))
                # print("lumiscale = "+str(lumiscale))
                #print("tree10.lumi_weight = "+str(tree10.lumi_weight))
                # print("self.DataLumi = "+str(self.DataLumi))
                #print("MCWeight(tree10, self.year, self.sample).getTotalWeight() = "+str(MCWeight(tree10, self.year, self.sample).getTotalWeight()))
                #print("self.gfltreff = "+str(self.gfltreff))
                # print("weight total = "+str(lumiscale * MCcorr*w_BRctau))
                
                #############
                var10['stopCtau'] = tree10.stopCtau 
                var10['MET'] = tree10.MET_pt
                # var10['MCWeight'] = MCWeight(tree10, self.year, self.sample).getTotalWeight()
                # var10['gfltreff'] = self.gfltreff
                # var10['lumiWeight'] = (tree10.lumi_weight)/1000.0
                # var10['w_BRctau'] = w_BRctau
                
                for key in histos10:
                    if key in var10.keys():
                        if var10[key] is not None:
                            if isinstance(var10[key], types.ListType):
                                for x in var10[key]: Fill1D(histos10[key], x, lumiscale * MCcorr * w_BRctau)
                            else:
                                #Fill1D(histos10[key], var10[key], lumiscale * MCcorr*w_BRctau)
                                #TEST REMOVE WHEN DONE
                                Fill1D(histos10[key], var10[key], lumiscale * MCcorr * w_BRctau)
                                ######
                        # else:
                        #     print("var10[key] is "+str(var10[key])+"  and key is "+str(key))
                    else:
                        print "You are trying to fill the histos for the keys", key, " which are missing in var10dictionary"
            else:
                n_rejected_10 +=1
        print("filled BR 1.0......")

        # print("Selected Entries in 0.3 histo "+str(selected_events03))
        # print("Selected Entries in 1.0 histo "+str(selected_events10))
        # print("rejected Entries in 0.3 histo "+str(n_rejected_03))
        # print("rejected Entries in 1.0 histo "+str(n_rejected_10))
        # print("Entries in 0.3 histo  "+str('MET')+"= "+str(histos03['MET'].GetEntries()))
        # print("Entries in 1.0 histo  "+str('MET')+"= "+str(histos10['MET'].GetEntries()))

        

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
            # print("Entries in 0.3 histo "+str(key_)+"= "+str(histos03[key_].GetEntries()))
            # print("Entries in 1.0 histo "+str(key_)+"= "+str(histos10[key_].GetEntries()))
            # print("Entries in combined histo = "+str(self.histos[key_].GetEntries()))
            # print("Integral in 0.3 histo = "+str(histos03[key_].Integral()))
            # print("Integral in 1.0 histo = "+str(histos10[key_].Integral()))
            # print("Integral in combined histo = "+str(self.histos[key_].Integral()))
            # print("......................")

            print("#####################################################")
            print("nentries_03.append("+ str(histos03[key_].GetEntries()) +")")
            print("nentries_10.append("+ str(histos10[key_].GetEntries()) +")")
            print("nentries_combined.append("+ str(self.histos[key_].GetEntries()) +")")

            print("integral_03.append("+ str(histos03[key_].Integral()) +")")
            print("integral_10.append("+ str(histos10[key_].Integral()) +")")
            print("integral_combined.append("+ str(self.histos[key_].Integral()) +")")

            print("nentries_03_rejected.append("+ str(n_rejected_03) +")")
            print("nentries_10_rejected.append("+ str(n_rejected_10) +")")
            print("#####################################################")
            row_csv_10 = [self.ms, self.ml, self.branching_ratio, histos10[key_].GetEntries(), n_rejected_10, histos10[key_].Integral()]
            row_csv_03 = [self.ms, self.ml, self.branching_ratio, histos03[key_].GetEntries(), n_rejected_03, histos03[key_].Integral()]
            row_csv_combined = [self.ms, self.ml, self.branching_ratio, self.histos[key_].GetEntries(), n_rejected_10+n_rejected_03, self.histos[key_].Integral()]
        


        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/info_test_10.csv", row_csv_10)
        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/info_test_03.csv", row_csv_03)
        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/info_test_combined.csv", row_csv_combined)

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