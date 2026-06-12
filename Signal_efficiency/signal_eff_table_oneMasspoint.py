from tabulate import tabulate

# Sample data
list1 = [66427+59820, 66427+59820, 66427+59820, 66427+59820, 66427+59820, 66427+59820, 66427+59820, 66427+59820, 66427+59820, 66427+59820]
list1_5 = [10826, 10826, 10826, 10826, 10826, 10826, 10826, 10826, 10826, 10826]

list2 = [116.475529556, 175.865424578, 226.66185062, 279.045277689, 343.260575294, 403.771128654, 443.32021755, 465.738231695, 487.699269168, 519.279375166]
rates = [a/float(b) for a, b in zip(list2, list1)]
efficiency = [100*(a/float(b)) for a, b in zip(list2, list1)]
print(efficiency)

# Custom column names
column_names = ["BR 0.1", "BR 0.2", "BR 0.3", "BR 0.4", "BR 0.5", "BR 0.6", "BR 0.7", "BR 0.8", "BR 0.9", "BR 1.0"]

table_data = [
    ["Nevents before selection"] + list1,
    ["Nentries after selection"] + list1_5,
    ["Nevents after selection"] + list2,
    ["after/before"] + rates,
    ["Signal efficiency (%)"] + efficiency
]

headers = [""] + column_names

print(tabulate(table_data, headers=headers, tablefmt="grid", floatfmt=".3f"))