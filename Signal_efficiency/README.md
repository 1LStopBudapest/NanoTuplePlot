# Signal efficiency tables and BR scan

Three small standalone scripts with their numbers hardcoded (they were filled in by hand from pipeline printouts, no inputs to point anywhere):

- `signal_eff_table.py` prints a table (via `tabulate`) of events before/after selection and the resulting efficiency for a handful of mass points.
- `signal_eff_table_oneMasspoint.py` is the same for a single point.
- `signal_eff_BR_plot.py` scatters the signal efficiency versus BR for the 300/280 point (`plot.png`).

A quick way to eyeball selection efficiencies from mid-2025; the systematic version of this across the whole grid is what `../preselection_efficiency/` produces now.
