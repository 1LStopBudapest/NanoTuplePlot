import os
import json
from tabulate import tabulate

# Folder where your JSON files are
folder = "./outputs_2018"

# Initialize accumulator dictionary
result = {}

nfiles = 100000
file_number = 0
# Loop over all JSON files in the folder
for filename in os.listdir(folder):

    file_number +=1
    if file_number>nfiles:
        break
    
    if filename.endswith(".json"):
        filepath = os.path.join(folder, filename)
        print(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)

        # Add values into result
        for key, value in data.items():
            if key not in result:
                # First time seeing this key then copy it
                result[key] = value
            else:
                # If it's a list, sum elementwise
                if isinstance(value, list):
                    result[key] = [a + b for a, b in zip(result[key], value)]
                # If it's a scalar, just sum
                else:
                    result[key] += value

print(result)
# Save the final dictionary
with open("summed_2018.json", "w") as f:
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

rows_per_block = 75  # rows in each vertical block
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
