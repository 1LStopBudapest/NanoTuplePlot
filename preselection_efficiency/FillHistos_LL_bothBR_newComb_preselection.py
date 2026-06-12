import ROOT
import types
import os, sys
import math
import numpy as np

sys.path.append('../../')
from Helper.VarCalc import *
from Helper.MCWeight import MCWeight
from Helper.GenFilterEff import GenFilterEff
from Helper.TreeVarSel_LL import TreeVarSel
#from Helper.TreeVarSel import TreeVarSel

sys.path.append('../')
from VarHandler import VarHandler


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

    def get_ctau_sample(self, BR_sample):
        c = 2.9979e11 # speed of light in mm per second
        hcut = 6.5821e-25
        # NOW scale properly to actual mStop
        decay_width_by_DeltaM_4bd_mstop500 = {10.:3.25e-17, 15.:3.52e-15, 20.:5.86e-14, 25.:4.48e-13, 30.:2.24e-12}
        delta_m_keys = sorted(decay_width_by_DeltaM_4bd_mstop500.keys())
        delta_m_vals = [decay_width_by_DeltaM_4bd_mstop500[k] for k in delta_m_keys]
        Delta_m = np.abs(self.ms-self.ml)
        idx = (np.abs(delta_m_keys - Delta_m)).argmin()
        width_500 = delta_m_vals[idx]
        decay_width_by_mstop_4bd = width_500 * (500.0 / self.ms)
        
        width_tot_true = decay_width_by_mstop_4bd/BR_sample

        true_ctau = (hcut/width_tot_true) * c
        return true_ctau

    def fill2(self):

        histos03 = {}
        histos10 = {}
        histos03_tail = {}
        histos10_tail = {}

        for name, h in self.histos.items():
            
            histos03[name] = h.Clone()
            histos10[name] = h.Clone()
            histos03_tail[name] = h.Clone()
            histos10_tail[name] = h.Clone()

        ctau_sample_03 = self.get_ctau_sample(0.3)
        ctau_sample_10 = self.get_ctau_sample(1.0)
        ctau_ratio_threshold = 7


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

        maxWeight10 = -10
        maxWeight03 = -10        

        for ientry03 in range(n_entries03):

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
                MCcorr = MCWeight(tree03, self.year, self.sample).getTotalWeight()

            
                
            var03= {key: None for key in vardic}#reseting the var03dictionary for each event
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel03 = TreeVarSel(tree03, self.isData, self.year, 'comb')
            #if getsel03.passFilters() and getsel03.PreSelection() and getsel03.Dxy2():
            #if getsel03.passFilters() and getsel03.PreSelection():
            #if getsel03.gen4Body():
            if getsel03.passFilters() and getsel03.PreSelection():

                selected_events03 = selected_events03+1

                weight_BRctau_list = tree03.ReweightBRctau
                w_BRctau = weight_BRctau_list[self.branching_ratio_index]

                #####################33
                if (tree03.stopCtau/ctau_sample_03) > ctau_ratio_threshold or (tree03.stopAntiCtau/ctau_sample_03) > ctau_ratio_threshold:
                    #Discard event
                    n_rejected_03 +=1
                    continue
                #######################

                if w_BRctau>maxWeight03:
                    maxWeight03=w_BRctau

                
                #############
                var03['stopCtau'] = tree03.stopCtau
                var03['MET'] = tree03.MET_pt
                
                for key in histos03:
                    if key == "stopCtauStack":
                        continue
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
                MCcorr = MCWeight(tree10, self.year, self.sample).getTotalWeight()
                
            var10= {key: None for key in vardic}#reseting the var10dictionary for each event
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel10 = TreeVarSel(tree10, self.isData, self.year, 'comb')
            #if getsel10.passFilters() and getsel10.PreSelection() and getsel10.Dxy2():
            #if getsel10.passFilters() and getsel10.PreSelection():
            #if getsel10.gen4Body():
            tail_event_10 = False

            if getsel10.passFilters() and getsel10.PreSelection():
            
                selected_events10 = selected_events10+1
                
                weight_BRctau_list = tree10.ReweightBRctau
                w_BRctau = weight_BRctau_list[self.branching_ratio_index]

                if w_BRctau > maxWeight10:
                    maxWeight10 = w_BRctau

                if (tree10.stopCtau/ctau_sample_03) > ctau_ratio_threshold or (tree10.stopAntiCtau/ctau_sample_03) > ctau_ratio_threshold:
                    tail_event_10 = True
                    #Division by ctau_sample_03 is not an error
                    #This makes the cut to have the same ctau cutting point for both samples
                    #This avoid an ugly step down in the final ctau distribution


                var10['stopCtau'] = tree10.stopCtau 
                var10['MET'] = tree10.MET_pt

                if tail_event_10:
                    for key in histos10_tail:
                        if key == "stopCtauStack":
                            continue
                        if key in var10.keys():
                            if var10[key] is not None:
                                if isinstance(var10[key], types.ListType):
                                    for x in var10[key]: Fill1D(histos10_tail[key], x, lumiscale * MCcorr * w_BRctau)
                                else:
                                    Fill1D(histos10_tail[key], var10[key], lumiscale * MCcorr * w_BRctau)
                        else:
                            print "You are trying to fill the histos for the keys", key, " which are missing in var10dictionary"
                else:
                    for key in histos10:
                        if key == "stopCtauStack":
                            continue
                        if key in var10.keys():
                            if var10[key] is not None:
                                if isinstance(var10[key], types.ListType):
                                    for x in var10[key]: Fill1D(histos10[key], x, lumiscale * MCcorr * w_BRctau)
                                else:
                                    Fill1D(histos10[key], var10[key], lumiscale * MCcorr * w_BRctau)
                        else:
                            print "You are trying to fill the histos for the keys", key, " which are missing in var10dictionary"
            else:
                n_rejected_10 +=1
        print("filled BR 1.0......")

        
        #######################################
        ##Histogram combination of the two BR
        ######################################
        for key_ in self.histos:

            if key_ == "stopCtauStack":
                continue

            term_03 = histos03[key_].Clone()
            term_03.Scale(1-self.branching_ratio)

            term_10 = histos10[key_].Clone()
            term_10.Scale(self.branching_ratio)

            term_10_tail = histos10_tail[key_].Clone()

            self.histos[key_].Add(term_03)
            self.histos[key_].Add(term_10)
            self.histos[key_].Add(term_10_tail)
            
            self.histos[key_].SetDirectory(self.hfile)

            # Now set the errors manually using error propagation
            for i in range(1, self.histos[key_].GetNbinsX() + 1):  # Loop through all bins (1 to NbinsX)
                error10 = histos10[key_].GetBinError(i)
                error03 = histos03[key_].GetBinError(i)
                error10_tail = histos10_tail[key_].GetBinError(i)
                
                # Calculate the propagated error: sqrt(error1^2 + error2^2)
                propagated_error_head = math.sqrt((self.branching_ratio**2)*(error10**2) + ((1-self.branching_ratio)**2)*(error03**2))
                propagated_error = math.sqrt((propagated_error_head**2) + (error10_tail**2))
                
                # Set the error for this bin in the sum histogram
                self.histos[key_].SetBinError(i, propagated_error)

            print("#####################################################")
            print("nentries_03.append("+ str(histos03[key_].GetEntries()) +")")
            print("nentries_10.append("+ str(histos10[key_].GetEntries()) +")")
            print("nentries_10_tail.append("+ str(histos10_tail[key_].GetEntries()) +")")
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
        
        

        his_03 = histos03["stopCtau"].Clone()
        his_03.Scale(1-self.branching_ratio)
        his_03.SetFillColor(ROOT.kGreen - 7)

        his_10 = histos10["stopCtau"].Clone()
        his_10.Scale(self.branching_ratio)
        his_10.SetFillColor(ROOT.kBlue - 7) 

        his_10_tail = histos10_tail["stopCtau"].Clone()
        his_10_tail.SetFillColor(ROOT.kRed - 7)          

        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/preselection_efficiency/info_test_new_comb_tight7_10.csv", row_csv_10)
        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/preselection_efficiency/info_test_new_comb_tight7_03.csv", row_csv_03)
        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/preselection_efficiency/info_test_new_comb_tight7_combined.csv", row_csv_combined)

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