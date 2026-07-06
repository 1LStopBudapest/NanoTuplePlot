import os
import json
from tabulate import tabulate
import math

# Folder where your JSON files are
folder = "./outputs_2016"

#Create dict with expected masspoints
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
num_mases_dict["large differences"] = 0.0

# Initialize accumulator dictionary
result = num_mases_dict

nfiles = 100000
file_number = 0
# Loop over all JSON files in the folder
for filename in os.listdir(folder):

    file_number +=1
    if file_number>nfiles:
        break
    
    if filename.endswith(".json"):
        filepath = os.path.join(folder, filename)
        #print(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)

        # Add values into result
        for key, value in data.items():

            if key in result:
                # If it's a list, sum elementwise
                if isinstance(value, list):
                    result[key][0] = result[key][0]+value[0]
                    result[key][1] = result[key][1]+value[1]
                # If it's a scalar, just sum
                else:
                    result[key] += value
            else:
                mstop, mx0 = key.split('_')
                mstop = int(mstop)
                mx0 = int(mx0)
                closest_key = []
                threshold = 3
                # print("key "+key)
                # print("mstop "+str(mstop))
                # print("mx0 "+str(mx0))
                # print("................")

                for mass_know in known_masspoints:
                    mstop_k, mx0_k = mass_know.split('_')
                    mstop_k = int(mstop_k)
                    mx0_k = int(mx0_k)
                    
                    diff = math.sqrt( (mstop-mstop_k)**2 + (mx0-mx0_k)**2 )

                    if diff<threshold:
                        closest_key.append(mass_know)
                #print(closest_key)
                if(len(closest_key)==0):
                    print("...NO CLOSEST KEY....")
                    print(key)
                    print(".......")
                elif (len(closest_key)>1):
                    print("...two or more CLOSEST KEYs....")
                else:
                    if isinstance(value, list):
                        result[closest_key[0]][0] = result[closest_key[0]][0]+value[0]
                        result[closest_key[0]][1] = result[closest_key[0]][1]+value[1]


print(result)
# Save the final dictionary
with open("summed.json", "w") as f:
    json.dump(result, f, indent=2)


###########################################################
#PRINT THE RESULTS AS A TABLE
###########################################################

# Example dictionary
data = result

# Separate list-valued and scalar keys
list_rows = []
scalar_rows = []
for key, value in data.items():
    if isinstance(value, list):
        list_rows.append([key] + value)
    else:
        scalar_rows.append([key, value])

# Function to chunk into row blocks
def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

rows_per_block = 35  # rows in each vertical block
chunks = list(chunk_list(list_rows, rows_per_block))

# Build tabulate table for each chunk
def make_table(chunk):
    max_cols = max(len(r) for r in chunk)
    padded = [r + [""] * (max_cols - len(r)) for r in chunk]
    #headers = ["Masspoint"] + [f"Val{i}" for i in range(1, max_cols)]
    headers = ["Masspoint"] + ["0.3"]+ ["1.0"]
    return tabulate(padded, headers=headers, tablefmt="grid").split("\n")

tables = [make_table(chunk) for chunk in chunks]

# Pad shorter tables so all have same height
max_height = max(len(t) for t in tables)
for t in tables:
    while len(t) < max_height:
        t.append(" " * len(t[0]))

# Concatenate list-valued tables side by side
side_by_side = ["   ".join(parts) for parts in zip(*tables)]
print("\n".join(side_by_side))

# Print scalar table below, if any
if scalar_rows:
    print("\nScalars:\n")
    print(tabulate(scalar_rows, headers=["Key", "Value"], tablefmt="grid"))



#Check nevents match
nevents_from_dict = 0
# Add values into result
for key, value in result.items():
    # If it's a list, sum elementwise
    if isinstance(value, list):
        nevents_from_dict = nevents_from_dict+value[0]
        nevents_from_dict = nevents_from_dict+value[1]

print("nevents_from_dict =  "+str(nevents_from_dict))

deltaM_10 = []
deltaM_rest = []
#Check average
for key, value in result.items():
    # If it's a list, sum elementwise
    if isinstance(value, list):
        mstop, mx0 = key.split('_')
        mstop = int(mstop)
        mx0 = int(mx0)
        deta_m = int(abs(mstop-mx0))

        if(deta_m==10):
            deltaM_10.append(value[0])
            deltaM_10.append(value[1])
        else:
            deltaM_rest.append(value[0])
            deltaM_rest.append(value[1])

avg_10 = sum(deltaM_10) / len(deltaM_10)
avg_rest = sum(deltaM_rest) / len(deltaM_rest)
print("average of masspoints with deltam 10 = "+str(avg_10))
print("average of masspoints with other deltam = "+str(avg_rest))