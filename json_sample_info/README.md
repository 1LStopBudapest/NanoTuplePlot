# Sample info JSONs

Merged JSON summaries of the splitted signal samples: available events per mass point and per generated BR (0.3 and 1.0), produced by the condor scans over the sample folders. One file per year (`summed_2016.json`, `summed_2017.json`, `summed_2018.json`), plus `summed_2018_reworked.json` for the reworked 2018 splitted samples.

The reworked file is the live one: `write_test_commands.py` in `../preselection_efficiency/` (and in `../CutFlow_study_LL/`) reads it to decide which mass points have enough events to be worth running and to generate the `execute_test.sh` job lists. Regenerating these files means rerunning the scan/merge machinery (see `../legacy_archive/check_met_eff/` for the old version and `../sample_reweighting/` for the current lxplus project).
