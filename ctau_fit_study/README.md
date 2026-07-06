# ctau fit study, validation of the BR/ctau reweighting

Finished study. This is where the `ReweightBRctau` scheme was validated: since the stop width depends on the 4-body branching ratio, reweighting an event to a different BR also has to reproduce the right ctau distribution. The scripts here fit exponentials to the reweighted ctau spectra and check that the BR=0.3 and BR=1.0 samples, once reweighted and combined, land on the expected lifetime.

The inputs are produced by the pair `1DPlot_LL_BR_weighted_bothBR.py` plus `FillHistos_LL_bothBR.py`, which was the state of the BR pipeline at the time: the simple two-term combination (1-BR)*h(0.3) + BR*h(1.0), before the ctau-tail handling was invented. `produce_ctau_plots.sh` runs it for a mass point over the BR range, then `plot_ctau_fit.py` (and `plot_ctau_fit_with_rel_err.py`, which adds relative-error handling) overlay and fit the resulting histograms. `produce_ctau_fit_plots_errors.sh` loops BR 0.1 to 1.0 for the 300/280 point.

The `plot_tree_*` scripts do the same kind of checks directly on trees instead of histograms, mostly on one-off `file_with_new_weight_*.root` files with hardcoded paths. `plot_tree_ctau_fit_combined.py` is the tree-level analogue of the both-BR combination, and `tree_Nevents_yield.py` computes expected yields from such a file.

The outcome of this study fed into the newComb combination now living in `preselection_efficiency/`. Kept for reference and in case the fits need to be reproduced, for example for the AN or thesis.

The imports were adjusted after the move: run the scripts from inside this folder, so the relative `sys.path` entries resolve. One thing to keep in mind is that several `plot_tree_*` scripts read hardcoded `file_with_new_weight_*.root` input paths that were already stale before the reorg, so check those individually if you ever rerun them.
