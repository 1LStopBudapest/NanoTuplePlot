import ROOT
import sys
import math
import os


sys.path.append('../')
from Sample.SampleChainSplitting import SampleChainSplitting
from array import array

# Helper: compute decay time (ct in mm)
def compute_ctau(pt, mass, vx, vy, prodvx, prodvy):
    Lxy = math.sqrt((vx - prodvx)**2 + (vy - prodvy)**2)
    ct = Lxy*mass / pt
    return ct

# Reweighting formula
def lifetime_weight(t, old_ctau, new_ctau):
    return (old_ctau / new_ctau) * ( math.exp(-t / new_ctau) / math.exp(-t / old_ctau))



true_br = 0.8
#true_br_for_ctau = 0.3
n_processed_events = 100000000
new_BR_targets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

valid_masses = [[250, 240], [300, 280], [325, 315], [350, 340], [350, 320], \
                [375, 365], [375, 355], [400, 390], [425, 400], [500, 490], \
                [525, 515], [550, 535], [600, 590], [600, 575], [650, 635], \
                [675, 665], [725, 715], [725, 705], [800, 790], [850, 840], \
                [900, 875], [925, 900], [975, 965], [1000, 990], [1075, 1065]]



folder_path = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/"
folder_path_out = "/big_data/LepStop/PostProcessedNtuple/displacedProcessedSamples/"

for filename in os.listdir(folder_path):
    full_path = os.path.join(folder_path, filename)
    if os.path.isfile(full_path):  # Optional: only process files
        print(full_path)
        print(filename)
        name, ext = os.path.splitext(filename)

        #to process only one
        # if(name != "SMS_T2tt_mStop_250to1100_dM_10to30_LL_57"):
        #     continue
        
        # Your processing code here
        print("#####################")
        print("#####################")

        for massList in valid_masses:

            for true_br_for_ctau in [0.3,1.0]:

                mStop = massList[0]
                mX0 = massList[1]
                Delta_m = abs(mStop-mX0)
                print("mstop = " + str(mStop))
                print("mx0 = " + str(mX0))
                print("Delta_m = " + str(Delta_m))
                print("..............................")

                tree_name = "Events"

                if true_br_for_ctau == 1.0:
                    true_br_for_ctau_str = "1.000"
                elif true_br_for_ctau == 0.3:
                    true_br_for_ctau_str = "0.300"

                output_file_name = name+"_"+str(mStop)+"_"+str(mX0)+"_"+true_br_for_ctau_str+"_processed"+ext
                output_file_path_full = os.path.join(folder_path_out, output_file_name)
                print(output_file_name)
                print(output_file_path_full)

                #true_ctau = 100  # mm
                # new_ctau = 10    # mm
                stop_pdgid = 1000006
                X0_pdgid = 1000022

                c = 2.9979e11 # speed of light in mm per second
                hcut = 6.5821e-25
                decay_width_by_DeltaM_4bd = {10.:2e-17, 15.:1e-15, 20.:5e-14, 25.:5e-13, 30.:2e-12}
                decay_width_by_DeltaM_4bd_mstop500 = {10.:3.25e-17, 15.:3.52e-15, 20.:5.86e-14, 25.:4.48e-13, 30.:2.24e-12}

                decay_width_by_mstop_4bd = (decay_width_by_DeltaM_4bd_mstop500[Delta_m] * 500 ) / mStop

                print(".............................")

                #width_tot_true = decay_width_by_DeltaM_4bd[Delta_m]/true_br_for_ctau
                width_tot_true = decay_width_by_mstop_4bd/true_br_for_ctau
                true_ctau = (hcut/width_tot_true) * c

                #Get a new ctau per each BR target and put them on a list
                new_ctau_targets = []
                for br_i in new_BR_targets:
                    #width_tot_new_i = decay_width_by_DeltaM_4bd[Delta_m]/br_i
                    width_tot_new_i = decay_width_by_mstop_4bd/br_i
                    new_ctau_targets.append((hcut/width_tot_new_i) * c) 

                # Open the ROOT file
                file = ROOT.TFile.Open(full_path)
                if not file or file.IsZombie():
                    print("Failed to open file: " + str(full_path))
                    exit(1)


                # Create output file
                f_out = ROOT.TFile(output_file_path_full, "RECREATE")
                

                print(".................................")
                print("ejecuta 1")
                print(".................................")

                # Get the TTree
                tree = file.Get(tree_name)
                if not tree:
                    print("TTree '" + str(tree_name) + "' not found in file.")
                    file.Close()
                    exit(1)

                #####
                #Cut mass and BR from input file
                ####
                # Define branch and alias names
                #First for the BR
                # This is for avoiding a bug in which branches with "1.000" or "0.300" in their names arent properly cutted
                real_name = "GenModel_T2tt_4bd_{0}_{1}".format(mStop, mX0)+"_"+true_br_for_ctau_str
                alias_name = "T2tt_{0}_{1}".format(mStop, mX0)
                # Create alias (this avoids ROOT parsing the dot as a float)
                tree.SetAlias(alias_name, real_name)
                #then for the mstop and mx0, no weird bug in here
                cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(mStop)+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(mX0)
                #cut2 = "Max$(@GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_"+true_br_for_ctau_str+")=="+str(1)
                #cut2 = "Max$(@GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_"+true_br_for_ctau_str+")=="+str(1)
                cut2 = "{0}==1".format(alias_name)
                cut3 = cut+"&&"+cut2
                #filtered_tree = tree.CopyTree(cut3)

                # First check if BR branch exists
                branch_name = real_name
                if not tree.GetBranch(branch_name):
                    print("Branch '{}' does not exist".format(branch_name))
                    continue

                try:
                    filtered_tree = tree.CopyTree(cut3)
                except:
                    print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                    print("Something went wrong")
                    print("BR value not found in file for given masspoint")
                    print("mstop = " + str(mStop))
                    print("mx0 = " + str(mX0))
                    print("BR not found = " + true_br_for_ctau_str)
                    print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                    file.Close()
                    continue
                

                
                # clone the filtered tree


                tree_out = filtered_tree.CloneTree(0)  # empty clone

                # Create branch for new weights
                weight_BRctau = array('f', [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0])
                stop_ctau = array('f', [-10.0])
                stop_decay_type = array('f', [-10.0])


                branch = tree_out.Branch("ReweightBRctau", weight_BRctau, "ReweightBRctau[10]/F")
                branch = tree_out.Branch("stopCtau", stop_ctau, "stopCtau/F")
                branch = tree_out.Branch("stopDecay", stop_decay_type, "stopDecay/F")



                total_events = filtered_tree.GetEntries()
                print("total events = " +str(total_events))

                nentry=0

                decay_mode = "inicialized variable"

                hist_ctau = ROOT.TH1F("hist_ctau", "hist_ctau", 100, 0, 20000)
                #hist_ctau = ROOT.TH1F("hist_ctau", "hist_ctau", 20, 0, 5)
                #Main event loop
                for entry in filtered_tree:
                    #Stop the loop if we process more events than allowed
                    if nentry > n_processed_events:
                        break
                    else:
                        nentry = nentry+1

                    #print("############################")
                    #print("event num"+str(nentry))
                    #print("############################")

                    #for debug
                    weight_ctau = []
                    weight_BR = []
                    #####

                    #################
                    # Check the decay mode of the stop pair
                    #################

                    decay_from_stop_idx = []
                    decay_from_stop_pdgid = []
                    decay_from_anti_stop_idx = []
                    decay_from_anti_stop_pdgid = []

                    #Error handling
                    weird_entry = False
                    
                    #Loop over particle index and pdig to identify the generated stops and when they decay
                    for i, pdgId in enumerate(entry.GenPart_pdgId):
                        #print("i = "+str(i)+" pdgId = "+str(pdgId)+" status = "+str(entry.GenPart_status[i]))

                        #Identify extrange error and trow  event
                        mother_idx_i = entry.GenPart_genPartIdxMother[i]
                        #print("mother_idx_i = "+str(mother_idx_i))
                        if mother_idx_i < -5:
                            print("----------------------------------------")
                            print("weird entry")
                            print("event num"+str(nentry))
                            print("----------------------------------------")
                            weird_entry = True
                            break
                        
                        #Identify stops generated
                        if pdgId == stop_pdgid:
                            mother_stop_idx = entry.GenPart_genPartIdxMother[i]
                            if entry.GenPart_pdgId[mother_stop_idx] != stop_pdgid and entry.GenPart_status[i] == 22:
                                stop_generated_idx = i

                        if pdgId == -stop_pdgid:
                            mother_anti_stop_idx = entry.GenPart_genPartIdxMother[i]
                            if entry.GenPart_pdgId[mother_anti_stop_idx] != -stop_pdgid and entry.GenPart_status[i] == 22:
                                stop_anti_generated_idx = i

                        #Identify stops decaying
                        if abs(pdgId) == X0_pdgid:
                            mother_x0_idx = entry.GenPart_genPartIdxMother[i]

                            if entry.GenPart_pdgId[mother_x0_idx] == stop_pdgid:
                                stop_decaying_idx = mother_x0_idx

                            if entry.GenPart_pdgId[mother_x0_idx] == -stop_pdgid:
                                stop_anti_decaying_idx = mother_x0_idx

                        #Identify all particles decaying from the stops
                        
                                                
                        if mother_idx_i!= -1 and entry.GenPart_pdgId[mother_idx_i] == stop_pdgid and pdgId != stop_pdgid and i not in decay_from_stop_idx:
                            mother_status_i = entry.GenPart_status[mother_idx_i]
                            if mother_status_i == 106:
                                decay_from_stop_idx.append(i)
                                decay_from_stop_pdgid.append(entry.GenPart_pdgId[i])

                        if mother_idx_i!= -1 and entry.GenPart_pdgId[mother_idx_i] == -stop_pdgid and pdgId != -stop_pdgid and i not in decay_from_anti_stop_idx:
                            mother_status_i = entry.GenPart_status[mother_idx_i]
                            if mother_status_i == 106:
                                decay_from_anti_stop_idx.append(i)
                                decay_from_anti_stop_pdgid.append(entry.GenPart_pdgId[i])

                    #Error handling
                    if weird_entry:
                        continue

                    #Check the type of decay based on the number of particles decaying from the stop
                    decay_type = "unknow"
                    if len(decay_from_stop_idx)==3 and len(decay_from_anti_stop_idx)==3:
                        decay_type = "4bd+4bd"
                    elif (len(decay_from_stop_idx)==3 and len(decay_from_anti_stop_idx)==2) or (len(decay_from_stop_idx)==2 and len(decay_from_anti_stop_idx)==3):
                        decay_type = "4bd+2bd"
                    elif len(decay_from_stop_idx)==2 and len(decay_from_anti_stop_idx)==2:
                        decay_type = "2bd+2bd"
                    else:
                        decay_type = "unknow"

                    decay_stop = "unknow"
                    if len(decay_from_stop_idx)==3:
                        decay_stop = "4bd"
                    elif len(decay_from_stop_idx)==2:
                        decay_stop = "2bd"
                    else:
                        decay_stop = "unknow"

                    decay_anti_stop = "unknow"
                    if len(decay_from_anti_stop_idx)==3:
                        decay_anti_stop = "4bd"
                    elif len(decay_from_anti_stop_idx)==2:
                        decay_anti_stop = "2bd"
                    else:
                        decay_anti_stop = "unknow"

                    #For debuggin
                    if decay_type == "unknow":
                        print("decays from stop idx = "+str(decay_from_stop_idx))
                        print("decays from anti stop idx = "+str(decay_from_anti_stop_idx))
                        print("decays from stop pdgid = "+str(decay_from_stop_pdgid))
                        print("decays from anti stop pdgid = "+str(decay_from_anti_stop_pdgid))
                        print("len stop = "+str(len(decay_from_stop_idx)))
                        print("len anti stop = "+str(len(decay_from_anti_stop_idx)))
                        print("decay_type = "+decay_type)
                        print("........")

                    #################
                    # Ctau reweighting
                    #################

                    # generated position for both stops
                    generated_vx_stop = entry.GenPart_vx[stop_generated_idx]
                    generated_vy_stop = entry.GenPart_vy[stop_generated_idx]
                    generated_vz_stop = entry.GenPart_vz[stop_generated_idx]

                    generated_vx_anti_stop = entry.GenPart_vx[stop_anti_generated_idx]
                    generated_vy_anti_stop = entry.GenPart_vy[stop_anti_generated_idx]
                    generated_vz_anti_stop = entry.GenPart_vz[stop_anti_generated_idx]

                    # Decay position for both stops
                    decay_vx_stop = entry.GenPart_vx[stop_decaying_idx]
                    decay_vy_stop = entry.GenPart_vy[stop_decaying_idx]
                    decay_vz_stop = entry.GenPart_vz[stop_decaying_idx]

                    decay_vx_anti_stop = entry.GenPart_vx[stop_anti_decaying_idx]
                    decay_vy_anti_stop = entry.GenPart_vy[stop_anti_decaying_idx]
                    decay_vz_anti_stop = entry.GenPart_vz[stop_anti_decaying_idx]

                    #mass and momentum of both stops
                    mass_stop = entry.GenPart_mass[stop_generated_idx]
                    mass_anti_stop = entry.GenPart_mass[stop_anti_generated_idx]
                    pt_stop = entry.GenPart_pt[stop_generated_idx]
                    pt_anti_stop = entry.GenPart_pt[stop_anti_generated_idx]

                    #pz_stop = entry.GenPart_pz[stop_generated_idx]

                    #For debugging
                    if decay_type == "unknow":
                        print("event")
                        print("decay_type = "+decay_type)
                        print("..generated vtx x ,y,z. stop decay into "+str(decay_stop))
                        print(generated_vx_stop)
                        print(generated_vy_stop)
                        print(generated_vz_stop)
                        print("..generated vtx x ,y,z. anti stop decay into "+str(decay_anti_stop))
                        print(generated_vx_anti_stop)
                        print(generated_vy_anti_stop)
                        print(generated_vz_anti_stop)
                        print("..decay vtx x ,y,z. stop decay into "+str(decay_stop))
                        print(decay_vx_stop)
                        print(decay_vy_stop)
                        print(decay_vz_stop)
                        print("..decay vtx x ,y,z. anti stop decay into "+str(decay_anti_stop))
                        print(decay_vx_anti_stop)
                        print(decay_vy_anti_stop)
                        print(decay_vz_anti_stop)

                    #print("decay_type = "+decay_type)
                    #Factor of 10 in decay and production lenght to convert cm to mm
                    ctau_stop = compute_ctau(pt_stop, mass_stop, decay_vx_stop*10, decay_vy_stop*10, generated_vx_stop*10, generated_vy_stop*10)
                    ctau_anti_stop = compute_ctau(pt_anti_stop, mass_anti_stop, decay_vx_anti_stop*10, decay_vy_anti_stop*10, generated_vx_anti_stop*10, generated_vy_anti_stop*10)
                    
                    Lxy = math.sqrt((generated_vx_stop*10 - decay_vx_stop*10)**2 + (generated_vy_stop*10 - decay_vy_stop*10)**2)
                    
                    if decay_stop=="4bd":
                        hist_ctau.Fill(ctau_stop)

                    for k in range(10):
                        weight_ctau_stop_k = lifetime_weight(ctau_stop, true_ctau, new_ctau_targets[k])
                        weight_ctau_anti_stop_k = lifetime_weight(ctau_anti_stop, true_ctau, new_ctau_targets[k])
                        weight_ctau_event_k = weight_ctau_stop_k*weight_ctau_anti_stop_k

                        weight_BR_stop_k = -1
                        weight_BR_anti_stop_k = -1
                        if decay_stop == "4bd":
                            weight_BR_stop_k = new_BR_targets[k]/true_br
                        elif decay_stop == "2bd":
                            weight_BR_stop_k = (1-new_BR_targets[k])/(1-true_br)
                        if decay_anti_stop == "4bd":
                            weight_BR_anti_stop_k = new_BR_targets[k]/true_br
                        elif decay_anti_stop == "2bd":
                            weight_BR_anti_stop_k = (1-new_BR_targets[k])/(1-true_br)
                        weight_BR_event_k = weight_BR_stop_k*weight_BR_anti_stop_k

                        weight_BRctau[k] = weight_BR_event_k*weight_ctau_event_k
                        #Only ctau reweight for testing
                        #weight_BRctau[k] = weight_ctau_event_k

                        #debug
                        weight_ctau.append(weight_ctau_event_k)
                        weight_BR.append(weight_BR_event_k)

                    stop_ctau[0] = ctau_stop

                    if decay_stop=="4bd":
                        stop_decay_type[0] = 4
                    elif decay_stop=="2bd":
                        stop_decay_type[0] = 2
                    else:
                        stop_decay_type[0] = -10
                    #print("weight_BRctau")
                    #print(weight_BRctau)
                    tree_out.Fill()
                    #

                #################
                # Write output
                #################

                tree_out.Write()
                f_out.Close()
                # Clean up, if using chain comment
                file.Close()


            print("finito eventino")