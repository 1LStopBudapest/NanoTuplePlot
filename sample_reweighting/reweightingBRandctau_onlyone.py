import ROOT
import sys
import math


sys.path.append('../')
from Sample.SampleChainSplitting import SampleChainSplitting
from array import array

# mStop = 250
# mX0 = 240
mStop = 250
mX0 = 240
Delta_m = abs(mStop-mX0)

true_br = 0.8
true_br_for_ctau = 0.3
n_processed_events = 1000000
new_BR_targets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


# File and branch info
#filename = "/big_data/LepStop/CentralFullNano/00EE1FC4-D27B-ED47-A567-F7B2E4C766B4.root"
#filename = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_LL_0.root"
#filename = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/joined_file_10.root"
filename = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_LL_57.root"

output_file = "./file_with_new_weight_BR_"+str(true_br_for_ctau)+"_mstop_"+str(mStop)+"_mX0_"+str(mX0)+".root"

tree_name = "Events"

if true_br_for_ctau == 1.0:
    true_br_for_ctau_str = "1.000"
elif true_br_for_ctau == 0.3:
    true_br_for_ctau_str = "0.300"

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

# Helper: compute decay time (ct in mm)
def compute_ctau(pt, mass, vx, vy, prodvx, prodvy):
    Lxy = math.sqrt((vx - prodvx)**2 + (vy - prodvy)**2)
    ct = Lxy*mass / pt
    return ct

# Reweighting formula
def lifetime_weight(t, old_ctau, new_ctau):
    return (old_ctau / new_ctau) * ( math.exp(-t / new_ctau) / math.exp(-t / old_ctau))



# Open the ROOT file
file = ROOT.TFile.Open(filename)
if not file or file.IsZombie():
    print("Failed to open file: " + str(filename))
    exit(1)
# Create output file
f_out = ROOT.TFile(output_file, "RECREATE")

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
#####
# cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(mStop)+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(mX0)
# cut2 = "Max$([GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_"+true_br_for_ctau_str+"])=="+str(1)
# cut3 = cut+"&&"+cut2
# filtered_tree = tree.CopyTree(cut3)

real_name = "GenModel_T2tt_4bd_{0}_{1}_0.300".format(mStop, mX0)
alias_name = "T2tt_{0}_{1}".format(mStop, mX0)
tree.SetAlias(alias_name, real_name)
cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=={0}&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=={1}".format(mStop, mX0)
cut2 = "{0}==1".format(alias_name)
cut3 = cut + "&&" + cut2

# First check if BR branch exists
branch_name = real_name
if not tree.GetBranch(branch_name):
    print("Branch '{}' does not exist".format(branch_name))



filtered_tree = tree.CopyTree(cut3)

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

    # print("############################")
    # print("event")
    # print("############################")

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

        #Identify extrange error
        mother_idx_i = entry.GenPart_genPartIdxMother[i]
        print("mother_idx_i = "+str(mother_idx_i))
        if mother_idx_i < -5:
            print("----------------------------------------")
            print("weird entry")
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

    print("event")
    #print("decay_type = "+decay_type)
    #Factor of 10 in decay and production lenght to convert cm to mm
    ctau_stop = compute_ctau(pt_stop, mass_stop, decay_vx_stop*10, decay_vy_stop*10, generated_vx_stop*10, generated_vy_stop*10)
    ctau_anti_stop = compute_ctau(pt_anti_stop, mass_anti_stop, decay_vx_anti_stop*10, decay_vy_anti_stop*10, generated_vx_anti_stop*10, generated_vy_anti_stop*10)
    print("pt_stop "+str(pt_stop))
    print("mass_stop "+str(mass_stop))
    print("decay_vx_stop "+str(decay_vx_stop*10))
    print("decay_vy_stop "+str(decay_vy_stop*10))
    print("generated_vx_stop "+str(generated_vx_stop*10))
    print("generated_vy_stop "+str(generated_vy_stop*10))
    Lxy = math.sqrt((generated_vx_stop*10 - decay_vx_stop*10)**2 + (generated_vy_stop*10 - decay_vy_stop*10)**2)
    print("Lxy "+str(Lxy))
    print("ctau_stop "+str(ctau_stop))
    print("true_ctau "+str(true_ctau))
    print("new_ctau_targets "+str(new_ctau_targets))
    print("stop decay into "+str(decay_stop))
    #print("ctau_anti_stop "+str(ctau_anti_stop))

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

    print("weight_ctau = "+str(weight_ctau))
    print("weight_BR = "+str(weight_BR))
    stop_ctau[0] = ctau_stop
    print("stop_ctau "+str(stop_ctau))

    if decay_stop=="4bd":
        stop_decay_type[0] = 4
    elif decay_stop=="2bd":
        stop_decay_type[0] = 2
    else:
        stop_decay_type[0] = -10
    #print("weight_BRctau")
    #print(weight_BRctau)
    tree_out.Fill() 
    


    """
    print("entry.GenPart_pdgId[stop_decaying_idx]) = "+str(entry.GenPart_pdgId[stop_decaying_idx]))
    print("entry.GenPart_status[stop_decaying_idx] = "+str(entry.GenPart_status[stop_decaying_idx]))
    print("entry.GenPart_pdgId[stop_anti_decaying_idx] = "+str(entry.GenPart_pdgId[stop_anti_decaying_idx]))
    print("entry.GenPart_status[stop_anti_decaying_idx] = "+str(entry.GenPart_status[stop_anti_decaying_idx]))

    print("........")

    print("entry.GenPart_pdgId[stop_generated_idx]) = "+str(entry.GenPart_pdgId[stop_generated_idx]))
    print("entry.GenPart_status[stop_generated_idx] = "+str(entry.GenPart_status[stop_generated_idx]))
    print("entry.GenPart_pdgId[mother generated stop]) = "+str(entry.GenPart_pdgId[ entry.GenPart_genPartIdxMother[stop_generated_idx]  ]))
    print("entry.GenPart_status[mother generated stop] = "+str(entry.GenPart_status[ entry.GenPart_genPartIdxMother[stop_generated_idx]  ]))
    
    print("entry.GenPart_pdgId[stop_anti_generated_idx] = "+str(entry.GenPart_pdgId[stop_anti_generated_idx]))
    print("entry.GenPart_status[stop_anti_generated_idx] = "+str(entry.GenPart_status[stop_anti_generated_idx]))
    print("entry.GenPart_pdgId[mother generated antistop]) = "+str(entry.GenPart_pdgId[ entry.GenPart_genPartIdxMother[stop_anti_generated_idx] ]))
    print("entry.GenPart_status[mother generated antistop] = "+str(entry.GenPart_status[ entry.GenPart_genPartIdxMother[stop_anti_generated_idx] ]))
 """

print("finito eventino")

canvas = ROOT.TCanvas()
hist_ctau.SetTitle("Stop ctau")
hist_ctau.GetXaxis().SetTitle("ctau mm")
hist_ctau.GetYaxis().SetTitle("Events")
#hist_ctau.Draw()
#canvas.SaveAs("hist_ctau.png")
#normalize hist
hist_ctau.Scale(1.0 / hist_ctau.Integral("width"))  # normalize to area = 1 (PDF)


#######
#fit_func = ROOT.TF1("fit_exp", "[0]*exp(-x/[1])", 0, 20000)  # adjust range as needed
fit_func = ROOT.TF1("fit_pdf", "(1.0 / [0]) * exp(-x / [0])", 1, 20000)
#fit_func.SetParameters(0, hist_ctau.GetMean())  # initial guesses: amplitude ctau
#

#fit_func = ROOT.TF1("fit_pdf", "(1.0 / [0]) * exp(-x / [0])", 0.05, 5)


fit_func.SetParameter(0, hist_ctau.GetBinCenter(hist_ctau.GetMaximumBin()))
#fit_func.SetParLimits(0, 1e-2, 1e5) 
fit_func.SetParLimits(0, 1e-2, 1e5) 


# Fit the histogram
hist_ctau.Fit(fit_func, "R")  # "R" = fit in specified range

# Extract fitted ctau value and uncertainty
fitted_ctau = fit_func.GetParameter(0)
fitted_ctau_err = fit_func.GetParError(0)

print("Fitted ctau = {:.2f} +- {:.2f} mm".format(fitted_ctau, fitted_ctau_err))

# Draw
canvas = ROOT.TCanvas("c", "c", 800, 600)
hist_ctau.Draw()
fit_func.SetLineColor(ROOT.kRed)
fit_func.Draw("SAME")
canvas.SaveAs("ctau_fit.png")

#################
# Write output
#################



tree_out.Write()
f_out.Close()
# Clean up, if using chain comment
file.Close()
