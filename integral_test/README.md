# Integral / expected-yield cross-checks

Standalone matplotlib scripts that read the CSVs produced by the BR-weighted pipeline and turn the histogram integrals into expected event counts, using the NNLO+NNLL cross sections (local copy of `stops_13TeV.py`) and the gen-filter efficiencies. They were used to sanity-check the yield formula and the isolation of mass points before the grid plots in `../preselection_efficiency/` took over that job.

- `integral_hist.py` reads `../Run_results_csv/info_test_new_comb_tight7_*.csv` and plots the combined/0.3/1.0 integrals.
- `4bd_expected_hist.py` computes the expected 4-body yields from the same kind of CSV.
- `integral_2bd_hist.py` does the analogous check for the 2-body contamination.
- `integral_iso_hist*.py` are variations looking at isolated mass points and different weight treatments.

Mind the input paths: some scripts point at `../Run_results_csv/` (still valid), but others still reference CSVs that used to sit loose at the top of `NanoTuplePlot/` and no longer exist there. Also, `Run_results_csv/` is scheduled to be removed; when that happens these scripts should be repointed to the current `info_test_new_comb_tight7_extra_*` CSVs in `../preselection_efficiency/`.
