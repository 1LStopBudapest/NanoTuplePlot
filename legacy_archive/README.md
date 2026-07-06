# Legacy archive

Old code that is superseded and kept only so nothing is lost while we're still cleaning up. Everything in here is a candidate for deletion once we're confident it's no longer needed, and git history keeps it recoverable anyway. Nothing in this folder should be run: besides being obsolete, the imports were not fixed after the move.

What's here:

- `LL_BR_gen1_single_BR/`, `LL_BR_gen3_genTest/`, `LL_BR_gen4_newComb_test/` hold the successive generations of the BR-weighted signal pipeline that led to the current one in `../preselection_efficiency/`. Each subfolder has a README explaining where it sits in that history. (The "gen 2" simple both-BR combination is not here, it lives in `../ctau_fit_study/` because the ctau fit study runs on its output.)
- `generated_artifacts/` holds job lists and shell scripts that the stack-plot drivers write on every run. Pure outputs, safe to delete any time.
- `check_met_eff/` and `sample_stop_LL_check_met_eff/` are two condor-based MET-efficiency scans over the signal grid (jobs, merged outputs and scatter plots included). Confirmed obsolete. They were built in the same lxplus/condor style as `../sample_reweighting/`, but unlike that one they are no longer used.
