# BR pipeline, generation 4: "newComb_test"

The direct predecessor of `../../preselection_efficiency/`, and the generation where the current combination scheme was born. `FillHistos_LL_bothBR_newComb_test.py` introduced `get_ctau_sample()` and the ctau-ratio tail cut at 7: tail events are dropped from the BR=0.3 chain and kept in a separate unscaled histogram from the BR=1.0 chain, giving the three-term combination (1-BR)*h(0.3) + BR*h(1.0) + h(1.0)_tail. It wrote the `info_test_new_comb_tight7_*.csv` files (the `tight` through `tight7` series in `../../Run_results_csv/` traces the tuning of that threshold).

What it did not yet have, and what the preselection version added: the real reco selection (`passFilters()` plus `PreSelection()`) instead of gen-level `gen4Body()` only, and the per-event decay-mode breakdown (4bd+4bd, 4bd+2bd, 2bd+2bd) that feeds the expected-yield formula. Apart from that, the driver and worker are essentially the same files as in `preselection_efficiency/`.

`write_test_commands.py`, `execute_test.sh` (a generated 259 KB command dump) and `monitest.sh` (a hand-written single-masspoint quick test, 675/665) are the scaffolding that drove this generation. Current copies live in `preselection_efficiency/`.
