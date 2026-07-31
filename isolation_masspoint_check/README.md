# Isolated mass point check

One script, `masspoint_isolation_check.py`, that reads the merged MET-efficiency JSON from the old condor scan (now at `../legacy_archive/check_met_eff/summed_2018.json`) and classifies the signal grid points, flagging the "isolated" ones (points that sit outside the regular grid pattern or have too few events to be usable). It produces matplotlib scatter plots of the grid.

This fed the mass-point filtering that `write_test_commands.py` in `../preselection_efficiency/` now does with its own deltaM and statistics cuts, so it is mostly of historical interest.
