from tabulate import tabulate

# Sample data
list1 = [66427+59820, 200000, 51251+45428, 48143+47910, 20267+38256, 38837+35451]
list2 = [10826, 3020, 9954, 7513, 7317, 9987]
rates = [a/float(b) for a, b in zip(list2, list1)]
efficiency = [100*(a/float(b)) for a, b in zip(list2, list1)]

# Custom column names
column_names = ["300_280", "325_315", "425_400", "550_535", "600_575", "900_875"]

table_data = [
    ["Nevents before selection"] + list1,
    ["Nevents after selection"] + list2,
    ["after/before"] + rates,
    ["Signal efficiency (%)"] + efficiency
]

headers = [""] + column_names

print(tabulate(table_data, headers=headers, tablefmt="grid", floatfmt=".3f"))