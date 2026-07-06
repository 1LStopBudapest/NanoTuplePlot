# Small standalone utilities

Grab-bag of one-file tools for poking at ntuples and samples. None of them are part of a pipeline, and most have a hardcoded input path near the top that you edit before running.

- `listBranches.py` lists the branches of a file.
- `SVexplorer.py` dumps the first SV_x values of a file.
- `uniqueValues.py` prints the unique values of a branch (was used on `GenModel_*` flags).
- `countEventsFolder.py` counts `Events` entries in every ROOT file of a folder.
- `simpleMassPlot.py` makes a quick histogram of a branch from one hardcoded signal file.
- `build_LL_sample_file.py` prints the `samples[...] = ...` dictionary lines to paste into a `Sample/FileList_LLStops_*` catalog for a list of mass points.
- `script_for_priya.py` prints GenPart mass-cut and `GenModel_T2tt_4bd_*` selection strings for a mass grid (made for a colleague).

Bigger branch-inspection scripts live in `../Branch_check/`. The last six tools here were moved from the top of `NanoTuplePlot/` during the 2026 reorg. They are self-contained (no `Sample`/`Helper` imports), so they should run as-is once their hardcoded paths point somewhere real.
