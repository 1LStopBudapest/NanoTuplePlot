# 2-body decay statistics test

One script, `masspoint_bd_hist.py`, that reads a BR-pipeline CSV and estimates, per mass point, the expected number of events where both stops decay to 4 bodies, together with the statistical significance of the deficit (the `sigmas_histogram.png` output). It was a quick check of how much 2-body contamination the samples carry, before the proper per-decay-mode bookkeeping was added to the preselection worker.

Note the input path still points to an `info_test.csv` that used to sit at the top of `NanoTuplePlot/` and was already gone before the reorg; the equivalent files live in `../Run_results_csv/`. Superseded by the decay-mode breakdown in `../preselection_efficiency/` (the `_extra` CSV columns), so mostly of historical interest.
