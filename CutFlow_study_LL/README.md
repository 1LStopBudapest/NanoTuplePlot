# Cut-flow study for the long-lived analysis

Work in progress. A fork of the BR-weighted newComb pipeline that, instead of variable histograms, fills a single cut-flow histogram by walking the selection sequentially (filters, MET cut, HT cut, ISR cut, tau veto, lepton cut, extra-lepton veto, extra-jet veto, dphi cut, search region) for every mass point and BR.

Same scaffold as `../preselection_efficiency/`: `write_test_commands.py` generates `execute_test.sh` (and `execute_test_mini.sh` is a small hand-made subset for quick checks), each job runs `1DPlot_LL_BR_weighted_bothBR_newComb_cutFlow.py` with the worker `FillHistos_LL_bothBR_newComb_cutFlow.py`, and the results are appended to `../Run_results_csv/info_test_cutFlow_*.csv`. The `plot_cutFlow*.py` scripts draw the per-point and integrated cut-flows; `plot_cutFlow_integrated_allBR.py` overlays the BR range.

`1DPlot_test_lepton_truth.py` and `FillHistos_test_lepton_truth.py` are a further fork studying the truth origin of the selected leptons.

This folder was not part of the July 2026 reorg and is being updated by the analyst directly, so leave it alone unless asked.
