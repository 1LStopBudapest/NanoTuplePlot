import ROOT
import sys
import pandas as pd
import json
import math

# sys.argv[0] is the script name
# sys.argv[1:] are the arguments passed from the console

if len(sys.argv) != 3:
    print("Usage: python stop_check_BR_branches_per_event.py /path/to/input_file.root /path/to/output_file.root")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]
n_processed_events = 200000

####################################################
#Create dictionary with all possible masses
known_masspoints = []
known_mStop = []
known_mX0 = []

#Check if all branches are there
delta_m_stop = 25
delta_m_x0 = [10,15,20,25,30]
nmasspoints = 0

for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        nmasspoints = nmasspoints+1
        known_masspoints.append(f"{mStop}_{mX0}")
        known_mStop.append(mStop)
        known_mX0.append(mX0)

num_mases_dict = {masspoint: [0.0,0.0] for masspoint in known_masspoints}
num_mases_dict["nEventsTotal"] = 0.0
num_mases_dict["strange masspoints"] = 0.0
num_mases_dict["orphans"] = 0.0
num_mases_dict["different stop antistop masses"] = 0.0
num_mases_dict["strange error"] = 0.0
num_mases_dict["strange event"] = 0.0
num_mases_dict["large differences"] = 0.0
#num_mases_dict["different X0 antiX0 masses"] = 0.0
known_mStop_original = known_mStop
known_masspoints_original = known_masspoints

#print(num_mases_dict)
######################################################

######################################################
#Open the root file and read the tree

# Open the ROOT file
root_file = ROOT.TFile.Open(input_file)
if not root_file or root_file.IsZombie():
    print(f"Error: Could not open file {input_file}")
    sys.exit(1)

# Get the Events tree
tree = root_file.Get("Events")
if not tree:
    print("Error: Could not find tree 'Events'")
    root_file.Close()
    sys.exit(1)
######################################################

######################################################
#Read all events and add to the dictionary
stop_pdgid = 1000006
X0_pdgid = 1000022
nentry = 0

for entry in tree:
    #print("----------event--------------------")
    # Get stop and x0 mass
    mass_stop = 0
    mass_X0 = 0

    # if nentry >= n_processed_events:
    #     break
    # else:
    #     nentry = nentry+1
    nentry = nentry+1

    num_mases_dict["nEventsTotal"] += 1
    
    if nentry % 1000==0 : print("event num"+str(nentry))

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

        """ if pdgId == X0_pdgid:
            mother_X0_idx = entry.GenPart_genPartIdxMother[i]
            if entry.GenPart_pdgId[mother_X0_idx] != X0_pdgid and entry.GenPart_status[i] == 1:
                X0_generated_idx = i

        if pdgId == -X0_pdgid:
            mother_anti_X0_idx = entry.GenPart_genPartIdxMother[i]
            if entry.GenPart_pdgId[mother_anti_X0_idx] != -X0_pdgid and entry.GenPart_status[i] == 1:
                X0_anti_generated_idx = i
        """
        if pdgId == abs(X0_pdgid):
            mother_X0_idx = entry.GenPart_genPartIdxMother[i]
            if entry.GenPart_pdgId[mother_X0_idx] != abs(X0_pdgid):
                X0_generated_idx = i

    #Error handling
    if weird_entry:
        continue

    
    #Catch a different weird entry
    try:
        mass_stop = entry.GenPart_mass[stop_generated_idx]
        mass_anti_stop = entry.GenPart_mass[stop_anti_generated_idx]
        mass_X0 = entry.GenPart_mass[X0_generated_idx]
    except:
        num_mases_dict["strange event"] += 1 
        continue
    #mass_anti_X0 = entry.GenPart_mass[X0_anti_generated_idx]

    

    masspoint_key = f"{mass_stop:.0f}_{mass_X0:.0f}"

    if (mass_stop not in known_mStop) or (mass_X0 not in known_mX0) or (masspoint_key not in known_masspoints):

        # print("---------STRANGE MASSPOINT------------")
        # print("mass_stop "+str(mass_stop))
        # print("mass_anti_stop "+str(mass_stop))
        # print("mass_X0 "+str(mass_X0))
        # print("masspoint_key "+masspoint_key)
        # #print("mass_anti_X0"+str(mass_anti_X0))
        # print("----------------------------------------")
        new_masspoint = f"{mass_stop:.0f}_{mass_X0:.0f}"
        num_mases_dict[new_masspoint] = [0.0,0.0]
        known_mStop.append(mass_stop)
        known_mX0.append(mass_X0)
        known_masspoints.append(masspoint_key)

    if mass_stop != mass_anti_stop:
        print("---------MSTOPS NOT EQUAL------------")
        num_mases_dict["different stop antistop masses"] += 1
        continue

    

    #BR_03_value = getattr(entry, branch_name03)
    #BR_10_value = getattr(entry, branch_name10)
    #print("BR_03_value "+str(BR_03_value))
    #print("BR_10_value "+str(BR_10_value))
    BR_03_value = False
    BR_10_value = False
    do_seach = False

    #We made the assumption that the BR branches names have multiples of 5 in their names
    if masspoint_key in known_masspoints_original:
        branch_name03 = f"GenModel_T2tt_4bd_{mass_stop:.0f}_{mass_X0:.0f}_0.300"
        branch_name10 = f"GenModel_T2tt_4bd_{mass_stop:.0f}_{mass_X0:.0f}_1.000"
        BR_03_found = False
        BR_10_found = False

        try:
            BR_03_value = getattr(entry, branch_name03)
            BR_03_found = True
        except:
            pass

        try:
            BR_10_value = getattr(entry, branch_name10)
            BR_10_found = True
        except:
            pass

        if BR_03_found and BR_10_found:
            if BR_03_value and BR_10_value:
                #One event cannot have both flags being true
                print("---------STRANGE ERROR 1-----------------")
                num_mases_dict["strange error"] += 1 
            elif BR_03_value:
                num_mases_dict[masspoint_key][0] += 1
            elif BR_10_value:
                num_mases_dict[masspoint_key][1] += 1
            else:
                #maybe is a mixed value masspoint, not an orphan
                do_seach = True
        elif BR_03_found:
            if BR_03_value:
                num_mases_dict[masspoint_key][0] += 1
        elif BR_10_found:
            if BR_10_value:
                num_mases_dict[masspoint_key][1] += 1
        else:
            do_seach = True
    else:
        do_seach = True

    BR_03_value_assigned = False
    BR_10_value_assigned = False
    

    if do_seach:
        #print("--do search-----------------")
        
        known_masspoint_assigned = ""
        
        for masspoint_s in known_masspoints_original:
            BR_03_found = False
            BR_10_found = False
            BR_03_value_ = False
            BR_10_value_ = False
            #print("masspoint_s "+masspoint_s)
            temp_branch_name03_ = "GenModel_T2tt_4bd_"+masspoint_s+"_0.300"
            temp_branch_name10_ = "GenModel_T2tt_4bd_"+masspoint_s+"_1.000"
            try:
                BR_03_value_ = getattr(entry, temp_branch_name03_)
                #print("BR_03_value_ = "+str(BR_03_value_))
                #print("temp_branch_name03_ = "+str(temp_branch_name03_))
                
                BR_03_found = True
            except:
                pass
            try:
                BR_10_value_ = getattr(entry, temp_branch_name10_)
                BR_10_found = True
            except:
                pass

            if BR_03_found and BR_10_found:
                if BR_03_value_ and BR_10_value_:
                    #One event cannot have both flags being true
                    print("---------STRANGE ERROR 2-----------------")
                    num_mases_dict["strange error"] += 1 
                elif BR_03_value_:
                    num_mases_dict[masspoint_key][0] += 1
                    if BR_03_value_assigned:
                        print("Multiassigment")
                    BR_03_value_assigned = True
                    known_masspoint_assigned = masspoint_s
                    #print("1")
                elif BR_10_value_:
                    num_mases_dict[masspoint_key][1] += 1
                    BR_10_value_assigned = True
                    known_masspoint_assigned = masspoint_s

            elif BR_03_found:
                #print("ever executed")
                if BR_03_value_:
                    num_mases_dict[masspoint_key][0] += 1
                    BR_03_value_assigned = True
                    known_masspoint_assigned = masspoint_s
                    #print("2")
            elif BR_10_found:
                if BR_10_value_:
                    num_mases_dict[masspoint_key][1] += 1
                    BR_10_value_assigned = True
                    known_masspoint_assigned = masspoint_s
        
        #print("BR_03_value_assigned = "+str(BR_03_value_assigned))
        #print("BR_10_value_assigned = "+str(BR_10_value_assigned))


    if (not BR_03_value and not BR_10_value) and (not BR_03_value_assigned and not BR_10_value_assigned):
        num_mases_dict["orphans"] += 1
        print("----------ORPHAN-----------------")
        print("mass_stop "+str(mass_stop))
        print("mass_x0 "+str(mass_X0))
        masspoint_orphan = f"{mass_stop:.0f}_{mass_X0:.0f}_orphan"
        if masspoint_orphan not in num_mases_dict.keys():
            #add new orphan masspoint
            num_mases_dict[masspoint_orphan] = 1.0
        else:
            num_mases_dict[masspoint_orphan] += 1

    #Evaluate if difference between found BR branch and real masspoint is large
    if do_seach:
        threshold_mass = 5
        mStop_BR, mX0_BR = known_masspoint_assigned.split('_')
        mStop_BR = int(mStop_BR)
        mX0_BR = int(mX0_BR)

        delta = math.sqrt( (mStop_BR-mass_stop)**2+(mX0_BR-mass_X0)**2  )

        if delta>threshold_mass:
            num_mases_dict["large differences"] += 1
            print("----------LARGE DIFFERENCES-----------------")
            print("mass_stop "+str(mass_stop))
            print("mass_x0 "+str(mass_X0))
            print("known_masspoint_assigned "+known_masspoint_assigned)





""" 

    if masspoint_key in known_masspoints:
        # print("----------------------------------------")
        # print("mass_stop "+str(mass_stop))
        # print("mass_anti_stop "+str(mass_stop))
        # print("mass_X0 "+str(mass_X0))
        # print("masspoint_key "+masspoint_key)
        # #print("mass_anti_X0"+str(mass_anti_X0))
        # print("----------------------------------------")

        branch_name03 = f"GenModel_T2tt_4bd_{mass_stop:.0f}_{mass_X0:.0f}_0.300"
        branch_name10 = f"GenModel_T2tt_4bd_{mass_stop:.0f}_{mass_X0:.0f}_1.000"

        try:
            BR_03_value = getattr(entry, branch_name03)
            #print("BR_03_value "+str(BR_03_value))
            if(BR_03_value):
                #print("BR_03_value "+str(BR_03_value))
                num_mases_dict[masspoint_key][0] += 1
        except:
            #print("No BR 0.3 branch for this event")
            for masspoint_pair in known_masspoints_original:
                try:
                    temp_branch_name03 = "GenModel_T2tt_4bd_"+masspoint_pair+"_0.300"
                    BR_03_value = getattr(entry, temp_branch_name03)
                    if(BR_03_value):
                        #print("BR_03_value "+str(BR_03_value))
                        num_mases_dict[masspoint_key][0] += 1
                        break
                except:
                    pass
            pass

        try:
            BR_10_value = getattr(entry, branch_name10)
            #print("BR_10_value "+str(BR_10_value))
            if(BR_10_value):
                #print("BR_10_value "+str(BR_10_value))
                num_mases_dict[masspoint_key][1] += 1
        except:
            #print("No BR 1.0 branch for this event")
            for masspoint_pair in known_masspoints_original:
                try:
                    temp_branch_name10 = "GenModel_T2tt_4bd_"+masspoint_pair+"_1.000"
                    BR_10_value = getattr(entry, temp_branch_name10)
                    if(BR_10_value):
                        #print("BR_03_value "+str(BR_03_value))
                        num_mases_dict[masspoint_key][1] += 1
                        break
                except:
                    pass
            pass

        if not BR_03_value and not BR_10_value:
            num_mases_dict["orphans"] += 1
            print("----------ORPHAN-----------------")
            print("mass_stop "+str(mass_stop))
            print("mass_x0 "+str(mass_X0))
            masspoint_orphan = f"{mass_stop:.0f}_{mass_X0:.0f}_orphan"
            if masspoint_orphan not in num_mases_dict.keys():
                #add new orphan masspoint
                num_mases_dict[masspoint_orphan] = 1.0
            else:
                num_mases_dict[masspoint_orphan] += 1
    else:
        print("---------STRANGE ERROR-----------------")
        print("masspoint key =")
        print(masspoint_key)
        num_mases_dict["strange error"] += 1 
 """
print(num_mases_dict)

# Close the ROOT file
root_file.Close()

#Check nevents match
nevents_from_dict = 0
# Add values into result
for key, value in num_mases_dict.items():
    # If it's a list, sum elementwise
    if isinstance(value, list):
        nevents_from_dict = nevents_from_dict+value[0]
        nevents_from_dict = nevents_from_dict+value[1]

print("nevents_from_dict =  "+str(nevents_from_dict))
###########################################


# Convert dictionary to pandas DataFrame
# df = pd.DataFrame(num_mases_dict)

# # Save to CSV
# df.to_json(output_file, orient="records")

with open(output_file, "w") as f:
    json.dump(num_mases_dict, f)

print(f"Results saved to {output_file}")
