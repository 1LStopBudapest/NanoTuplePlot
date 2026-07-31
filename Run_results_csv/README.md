# Old run results (to be removed)

Accumulated CSV outputs of the older BR-pipeline generations: the `info_test_*` series from the genTest generation, the `info_test_cutFlow_*` files from the cut-flow study, and the `info_test_new_comb_tight*` series that traces the tuning of the ctau-tail threshold (from `tight` up to the final `tight7`).

The analyst will remove this folder himself. Until then, be aware that `../integral_test/` still reads `info_test_new_comb_tight7_*` from here and `../CutFlow_study_LL/` still appends to the `info_test_cutFlow_*` files. The current pipeline writes its CSVs inside `../preselection_efficiency/` instead.
