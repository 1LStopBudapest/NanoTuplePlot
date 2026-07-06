# BR pipeline, generation 3: "genTest"

A debugging generation of the both-BR combination. `1DPlot_LL_BR_weighted_bothBR_genTest.py` plus `FillHistos_LL_bothBR_genTest.py` still use the simple two-term combination (1-BR)*h(0.3) + BR*h(1.0), but the selection was relaxed to gen-level only (`gen4Body()`, no reco preselection), and this is where the pipeline started dumping per-masspoint CSVs (`info_test_{03,10,combined}.csv`, the oldest files now sitting in `../../Run_results_csv/`). `execute_1D_plots.sh` is the hand-made command dump that drove it.

Superseded by the newComb generation (ctau-tail handling) and then by `../../preselection_efficiency/`.
