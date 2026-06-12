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

# ===================================================================
# Helper function: Check if a generated lepton comes from the stop decay chain
# ===================================================================
def is_from_stop(gen_lep, tree, stop_pdgId=1000006, max_steps=20, print_parents=False):
    """
    Walks upwards through mother indices to see if this lepton originates from the stop.
    stop_pdgId: usually 1000006 (stop1) or -1000006 (anti-stop). 
                You can also pass a list if needed.
    """
    if isinstance(stop_pdgId, int):
        stop_pdgId = [stop_pdgId, -stop_pdgId]
    
    current_idx = gen_lep["genIdx"]
    steps = 0
    if print_parents:
        print("lepton inheritance:")
    while current_idx >= 0 and steps < max_steps:
        pdgid = tree.GenPart_pdgId[current_idx]
        if print_parents:
            print("pdgid = "+str(pdgid))
        
        # If we reach a stop, this lepton is from the signal
        if abs(pdgid) in stop_pdgId:
            return True
        
        # Move to mother
        
        current_idx = tree.GenPart_genPartIdxMother[current_idx]
        steps += 1
    return False

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

        #histos03 = self.histos.copy()
        #histos10 = self.histos.copy()

        histos03 = {}
        histos10 = {}
        histos03_tail = {}
        histos10_tail = {}

        for name, h in self.histos.items():
            
            histos03[name] = h.Clone()
            #histos03[name].Reset()

            histos10[name] = h.Clone()
            #histos10[name].Reset()
            histos03_tail[name] = h.Clone()
            histos10_tail[name] = h.Clone()

        ctau_sample_03 = self.get_ctau_sample(0.3)
        ctau_sample_10 = self.get_ctau_sample(1.0)
        ctau_ratio_threshold = 7

        #################################################
        # print("hist1 pointer:", histos03)
        # print("hist2 pointer:", histos10)
        # print("hist2_tail pointer:", histos10_tail)
        #################################################

        selected_events03 = 0
        selected_events10 = 0

        n_rejected_03 = 0
        n_rejected_10 = 0

        maxWeight10 = -10
        maxWeight03 = -10

        #########################
        #Fill tree with chain from BR 03
        ##########################
        tree03 = self.chain03

        vardic = self.vardic
        n_entries03 = tree03.GetEntries()
        nevtcut03 = n_entries03 -1 if self.nEvents == - 1 else self.nEvents - 1
        print 'Running over total events: ', nevtcut03+1

        n_matched_events = 0


        for ientry03 in range(n_entries03):

            if ientry03 > nevtcut03: break
            if ientry03 % (nevtcut03/10)==0 : print 'processing ', ientry03,'th event'

            tree03.GetEntry(ientry03)
            if self.isData:
                lumiscale = 1.0
            else:
                lumiscale = (self.DataLumi) * (tree03.lumi_weight)/1000.0
            if self.isData or self.NoCorr:
                MCcorr = 1.0
            else:
                MCcorr = MCWeight(tree03, self.year, self.sample).getTotalWeight()
                
            var03= {key: None for key in vardic}#reseting the var03dictionary for each event
            bin_to_fill = -5
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel03 = TreeVarSel(tree03, self.isData, self.year, 'comb')

            if True:

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


                #######################################################
                ### Extract final gen leptons

                final_leptons = []          # list of dicts (or you can use TLorentzVector, etc.)
                pt_cut_gen = 1
                eta_cut_gen = 2.5

                for i in range(tree03.nGenPart):
                    pdgid  = tree03.GenPart_pdgId[i]
                    status = tree03.GenPart_status[i]
                    pt     = tree03.GenPart_pt[i]
                    eta    = tree03.GenPart_eta[i]
                    motherIdx = tree03.GenPart_genPartIdxMother[i]
                    #print(motherIdx)
                    if motherIdx>0:
                        motherPdgId = tree03.GenPart_pdgId[motherIdx]
                    else:
                        motherPdgId = -1
                    #print(motherPdgId)
                    stop_pdgid = 1000006

                    if (status == 1 and
                        abs(pdgid) in (11, 13, 15) 
                        and pt > pt_cut_gen
                        and abs(eta)<eta_cut_gen
                        #and abs(motherPdgId)==stop_pdgid
                        ):

                        final_leptons.append({
                            "pdgId" : pdgid,
                            "pt"    : pt,
                            "eta"   : tree03.GenPart_eta[i],
                            "phi"   : tree03.GenPart_phi[i],
                            "mass"  : tree03.GenPart_mass[i],
                            "genIdx"     : i,
                            # add more variables if you need them (mother index, statusFlags, ...)
                        })

                #######################################################

                # ===================================================================
                # Mark which gen leptons come from the stop (Ancestry Tracing)
                # ===================================================================
                n_lep_from_stop = 0
                for gen_lep in final_leptons:
                    gen_lep["fromStop"] = is_from_stop(gen_lep, tree03, stop_pdgId=1000006)

                    if is_from_stop(gen_lep, tree03, stop_pdgId=1000006):
                        n_lep_from_stop+=1
                
                if n_lep_from_stop>2:
                    print("............")
                    print("n_lep_from_stop = "+str(n_lep_from_stop))
                    for gen_lep in final_leptons:
                        if gen_lep["fromStop"]:
                            dumb = is_from_stop(gen_lep, tree03, stop_pdgId=1000006,print_parents=True)
                ############################################################


                if len(final_leptons)>=1:

                    var03['nLeptonGen'] = len(final_leptons)

                    ###################################################################

                    n_lepton_measured_03 = len(getsel03.getLepVar(getsel03.selectMuIdx()))
                    var03['nLeptonMeasured'] = n_lepton_measured_03
                    
                    # ===================================================================
                    # DeltaR Matching for the leading reconstructed lepton
                    # ===================================================================

                    sorted_leps = getsel03.getSortedLepVar()
                    truth_matched_lepton = False
                    best_deltaR = 999.0
                    matched_gen_lep = None

                    if len(sorted_leps) > 0:
                        reco = sorted_leps[0]                     # highest-pT selected lepton
                        reco_eta = reco.get('eta', 0.0)
                        reco_phi = reco.get('phi', 0.0)
                        reco_pt = reco.get('pt', 0.0)
                        tp       = reco['type']
                        reco_idx = reco['idx']

                        # Optional: still read the old genPartFlav for comparison
                        if tp == 'mu':
                            old_flag = ord(tree03.Muon_genPartFlav[reco_idx]) if hasattr(tree03, 'Muon_genPartFlav') else -1
                        elif tp == 'Electron':
                            old_flag = ord(tree03.Electron_genPartFlav[reco_idx]) if hasattr(tree03, 'Electron_genPartFlav') else -1
                        else:
                            old_flag = ord(tree03.LowPtElectron_genPartFlav[reco_idx]) if hasattr(tree03, 'LowPtElectron_genPartFlav') else -1

                        # === DeltaR matching loop ===
                        for gen_lep in final_leptons:
                            # Simple flavor check first
                            if (tp == 'mu' and abs(gen_lep["pdgId"]) != 13) or \
                            (tp != 'mu' and abs(gen_lep["pdgId"]) != 11):
                                continue

                            d_eta = reco_eta - gen_lep["eta"]
                            d_phi = reco_phi - gen_lep["phi"]
                            # Correct phi difference for 2pi periodicity
                            d_phi = (d_phi + math.pi) % (2 * math.pi) - math.pi
                            
                            deltaR = math.sqrt(d_eta*d_eta + d_phi*d_phi)

                            if deltaR < best_deltaR:
                                best_deltaR = deltaR
                                matched_gen_lep = gen_lep
                                matched_reco_pt = reco_pt
                                gen_lep["genPartFlav"] = old_flag   # update for diagnostic

                        # Decision: is this lepton truth-matched to a generated lepton?
                        

                        if matched_gen_lep is not None and best_deltaR < 0.01:        # you can tune this threshold
                            is_signal = matched_gen_lep["fromStop"]
                            if is_signal:
                                truth_matched_lepton = True
                                # print("Leading lepton is truth-matched | DeltaR = " + str(round(best_deltaR, 4)) + 
                                #     " | gen pdgId = " + str(matched_gen_lep["pdgId"]) + 
                                #     " | gen pt = " + str(round(matched_gen_lep["pt"], 2)))
                                var03['truthMatchedLepton'] = 8  
                            else:
                                truth_matched_lepton = False
                                # print("Leading lepton NOT truth-matched | best DeltaR = " + str(round(best_deltaR, 4)))
                                var03['truthMatchedLepton'] = 4
                        else:
                            truth_matched_lepton = False
                            # print("Leading lepton NOT truth-matched | best DeltaR = " + str(round(best_deltaR, 4)))
                            var03['truthMatchedLepton'] = 4

                    else:
                        # print("No selected lepton in this event")
                        var03['truthMatchedLepton'] = 1
                        
                        # n_signal_taus = 0
                        # for gen_lep in final_leptons:
                        #     # Simple flavor check first
                            
                        #     if abs(gen_lep["pdgId"]) == 15:
                        #         is_signal_ = gen_lep["fromStop"]
                        #         if is_signal_:
                        #             n_signal_taus+=1
                        
                    
                    cuts = [
                        getsel03.lepcut,
                    ]

                    bin_to_fill = 0
                    for i, cut_method in enumerate(cuts):
                        if cut_method():          # call the method
                            bin_to_fill = i + 1
                        else:
                            break
                    
                    #############
                    var03['cutFlow'] = bin_to_fill
                    #######################################
                    if truth_matched_lepton:
                        var03["2Dpt"] = []
                        var03["2Dpt"].append(matched_gen_lep["pt"])
                        var03["2Dpt"].append(matched_reco_pt)
                    
                    ##########################################
                    for key in histos03:
                        if key == "stopCtauStack" or key == "2Dpt":
                            continue
                        if key in var03.keys():
                            if var03[key] is not None:
                                if isinstance(var03[key], types.ListType):
                                    #print("EXEC::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                                    for x in var03[key]: Fill1D(histos03[key], x, lumiscale * MCcorr * w_BRctau)
                                else:
                                    #print("EXEC2::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                                    Fill1D(histos03[key], var03[key], lumiscale * MCcorr * w_BRctau)
                        else:
                            print "You are trying to fill the histos for the keys", key, " which are missing in var03dictionary"
                    
                    if truth_matched_lepton:
                        Fill2D(histos03["2Dpt"], var03["2Dpt"][0], var03["2Dpt"][1], lumiscale * MCcorr * w_BRctau)
                        n_matched_events+=1
            else:
                n_rejected_03 +=1
        print("filled BR 0.3......")
        print("Entries in 0.3 histo  "+str('cutFlow')+"= "+str(histos03['cutFlow'].GetEntries()))

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
            else:
                lumiscale = (self.DataLumi) * (tree10.lumi_weight)/1000.0

            if self.isData or self.NoCorr:
                MCcorr = 1.0
            else:
                MCcorr = MCWeight(tree10, self.year, self.sample).getTotalWeight()
                
            var10= {key: None for key in vardic}#reseting the var10dictionary for each event
            bin_to_fill = -5
            #its a string: 'Std' for standard PF ele, 'LowpT' for low pT ele and 'comb' for combination of both starting from the object according to the given preference 
            getsel10 = TreeVarSel(tree10, self.isData, self.year, 'comb')

            tail_event_10 = False

            if True:
            
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

                ###########################################################################################
                ### Extract final gen leptons

                final_leptons = []          # list of dicts (or you can use TLorentzVector, etc.)
                pt_cut_gen = 1
                eta_cut_gen = 2.5

                for i in range(tree10.nGenPart):
                    pdgid  = tree10.GenPart_pdgId[i]
                    status = tree10.GenPart_status[i]
                    pt     = tree10.GenPart_pt[i]
                    eta    = tree10.GenPart_eta[i]
                    motherIdx = tree10.GenPart_genPartIdxMother[i]
                    if motherIdx>0:
                        motherPdgId = tree10.GenPart_pdgId[motherIdx]
                    else:
                        motherPdgId = -1
                        
                    stop_pdgid = 1000006

                    if (status == 1 and
                        abs(pdgid) in (11, 13, 15) 
                        and pt > pt_cut_gen
                        and abs(eta)<eta_cut_gen
                        #and abs(motherPdgId)==stop_pdgid
                        ):

                        final_leptons.append({
                            "pdgId" : pdgid,
                            "pt"    : pt,
                            "eta"   : tree10.GenPart_eta[i],
                            "phi"   : tree10.GenPart_phi[i],
                            "mass"  : tree10.GenPart_mass[i],
                            "genIdx"     : i,
                            # add more variables if you need them (mother index, statusFlags, ...)
                        })
                
                #######################################################

                # ===================================================================
                # Mark which gen leptons come from the stop (Ancestry Tracing)
                # ===================================================================
                
                for gen_lep in final_leptons:
                    gen_lep["fromStop"] = is_from_stop(gen_lep, tree10, stop_pdgId=1000006)

                if len(final_leptons)>=1:

                    var10['nLeptonGen'] = len(final_leptons)

                    ###############################################################
                    n_lepton_measured_10 = len(getsel10.getLepVar(getsel10.selectMuIdx()))
                    var10['nLeptonMeasured'] = n_lepton_measured_10

                    ####################################################

                    # ===================================================================
                    # DeltaR Matching for the leading reconstructed lepton
                    # ===================================================================

                    sorted_leps = getsel10.getSortedLepVar()
                    truth_matched_lepton = False
                    best_deltaR = 999.0
                    matched_gen_lep = None

                    if len(sorted_leps) > 0:
                        reco = sorted_leps[0]                     # highest-pT selected lepton
                        reco_eta = reco.get('eta', 0.0)
                        reco_phi = reco.get('phi', 0.0)
                        reco_pt = reco.get('pt', 0.0)
                        tp       = reco['type']
                        reco_idx = reco['idx']

                        # Optional: still read the old genPartFlav for comparison
                        if tp == 'mu':
                            old_flag = ord(tree10.Muon_genPartFlav[reco_idx]) if hasattr(tree10, 'Muon_genPartFlav') else -1
                        elif tp == 'Electron':
                            old_flag = ord(tree10.Electron_genPartFlav[reco_idx]) if hasattr(tree10, 'Electron_genPartFlav') else -1
                        else:
                            old_flag = ord(tree10.LowPtElectron_genPartFlav[reco_idx]) if hasattr(tree10, 'LowPtElectron_genPartFlav') else -1

                        # === DeltaR matching loop ===
                        for gen_lep in final_leptons:
                            # Simple flavor check first
                            if (tp == 'mu' and abs(gen_lep["pdgId"]) != 13) or \
                            (tp != 'mu' and abs(gen_lep["pdgId"]) != 11):
                                continue

                            d_eta = reco_eta - gen_lep["eta"]
                            d_phi = reco_phi - gen_lep["phi"]
                            # Correct phi difference for 2pi periodicity
                            d_phi = (d_phi + math.pi) % (2 * math.pi) - math.pi
                            
                            deltaR = math.sqrt(d_eta*d_eta + d_phi*d_phi)

                            if deltaR < best_deltaR:
                                best_deltaR = deltaR
                                matched_gen_lep = gen_lep
                                matched_reco_pt = reco_pt
                                gen_lep["genPartFlav"] = old_flag   # update for diagnostic

                        # Decision: is this lepton truth-matched to a generated lepton?

                        if matched_gen_lep is not None and best_deltaR < 0.01:        # you can tune this threshold
                            is_signal = matched_gen_lep["fromStop"]
                            if is_signal:
                                truth_matched_lepton = True
                                # print("Leading lepton is truth-matched | DeltaR = " + str(round(best_deltaR, 4)) + 
                                #     " | gen pdgId = " + str(matched_gen_lep["pdgId"]) + 
                                #     " | gen pt = " + str(round(matched_gen_lep["pt"], 2)))
                                var10['truthMatchedLepton'] = 8
                            else:
                                truth_matched_lepton = False
                                # print("Leading lepton NOT truth-matched | best DeltaR = " + str(round(best_deltaR, 4)))
                                var10['truthMatchedLepton'] = 4
                        else:
                            truth_matched_lepton = False
                            # print("Leading lepton NOT truth-matched | best DeltaR = " + str(round(best_deltaR, 4)))
                            var10['truthMatchedLepton'] = 4

                    else:
                        # print("No selected lepton in this event")
                        var10['truthMatchedLepton'] = 1                                       

                    #########################################################
                    

                    cuts = [
                        getsel10.lepcut,
                    ]

                    bin_to_fill = 0
                    for i, cut_method in enumerate(cuts):
                        if cut_method():          # call the method
                            bin_to_fill = i + 1
                        else:
                            break
                    

                    #############
                    var10['cutFlow'] = bin_to_fill
                    #########################################
                    if truth_matched_lepton:
                        var10["2Dpt"] = []
                        var10["2Dpt"].append(matched_gen_lep["pt"])
                        var10["2Dpt"].append(matched_reco_pt)
                    #############################################

                    if tail_event_10:
                        for key in histos10_tail:
                            if key == "stopCtauStack" or key == "2Dpt":
                                continue
                            if key in var10.keys():
                                if var10[key] is not None:
                                    if isinstance(var10[key], types.ListType):
                                        for x in var10[key]: Fill1D(histos10_tail[key], x, lumiscale * MCcorr * w_BRctau)
                                    else:
                                        Fill1D(histos10_tail[key], var10[key], lumiscale * MCcorr * w_BRctau)
                            else:
                                print "You are trying to fill the histos for the keys", key, " which are missing in var10dictionary"
                        if truth_matched_lepton:
                            Fill2D(histos10["2Dpt"], var10["2Dpt"][0], var10["2Dpt"][1], lumiscale * MCcorr * w_BRctau)
                            n_matched_events+=1
                    else:
                        for key in histos10:
                            if key == "stopCtauStack" or key == "2Dpt":
                                continue
                            if key in var10.keys():
                                if var10[key] is not None:
                                    if isinstance(var10[key], types.ListType):
                                        for x in var10[key]: Fill1D(histos10[key], x, lumiscale * MCcorr * w_BRctau)
                                    else:
                                        Fill1D(histos10[key], var10[key], lumiscale * MCcorr * w_BRctau)
                            else:
                                print "You are trying to fill the histos for the keys", key, " which are missing in var10dictionary"
                        if truth_matched_lepton:
                            Fill2D(histos10["2Dpt"], var10["2Dpt"][0], var10["2Dpt"][1], lumiscale * MCcorr * w_BRctau)
                            n_matched_events+=1
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
            row_csv_10 = [self.ms, self.ml, self.branching_ratio, histos10[key_].GetEntries(), n_rejected_10, histos10[key_].Integral(), maxWeight10]
            row_csv_03 = [self.ms, self.ml, self.branching_ratio, histos03[key_].GetEntries(), n_rejected_03, histos03[key_].Integral(), maxWeight03]
            row_csv_combined = [self.ms, self.ml, self.branching_ratio, self.histos[key_].GetEntries(), n_rejected_10+n_rejected_03, self.histos[key_].Integral()]
        

        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/Run_results_csv/info_test_cutFlow_10.csv", row_csv_10)
        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/Run_results_csv/info_test_cutFlow_03.csv", row_csv_03)
        append_row_to_csv("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/Run_results_csv/info_test_cutFlow_combined.csv", row_csv_combined)

        print("Combined histograms of the two BR......")
        print("n_matched_events = "+str(n_matched_events))
                
        #print(type(histos10["stopCtau"] * 2))
        print("wwwwwwwwwwwwwwwwwwwwwwwwww")
        """ print(self.histos)
        for keyes in self.histos:
            print(keyes)
            print(self.histos[keyes].Print("all"))

            # Check if the histogram is valid
            if self.histos[keyes].GetEntries() == 0:
                print("Error: Histogram is empty.") """


        print("wwwwwwwwwwwwwwwwwwwwwwwwww")