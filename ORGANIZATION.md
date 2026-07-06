# NanoTuplePlot folder organization

Reorganized July 2026: the loose top-level scripts were sorted into per-pipeline subfolders. Files were only moved, never edited, so every moved script still has the `sys.path` and relative paths of its old location and will not run until those are fixed (see the last section). Each subfolder has its own README explaining what it does and how it runs.

## Folder map

| Folder | What it is | Status |
|---|---|---|
| `preselection_efficiency/` | BR-weighted signal grid: preselection efficiency and expected yields (newComb combination, decay-mode breakdown) | Canonical, active. Untouched by the reorg |
| `CutFlow_study_LL/` | Cut-flow study on the BR-weighted pipeline | Work in progress (untouched) |
| `integral_test/` | Integral/yield cross-checks reading the BR-pipeline CSVs | Active-ish, still reads `Run_results_csv/` (see below) |
| `sample_reweighting/` | Separate project: adds the `ReweightBRctau` branches to the input nanoAODs, adapted for lxplus and a newer Python | Do not touch from here |
| `stack_plots_LL/` | Data/MC stack plots for the LL analysis (comb/std/lowPt electrons) | Active, candidate for newComb signal update |
| `1D_plots_LL/` | Quick 1D histograms of a single sample (LL selection) plus overlay scripts | Active generic tool |
| `ctau_fit_study/` | Validation of the BR/ctau reweighting (fits to reweighted ctau spectra), including its input producer (the old simple both-BR combination) | Finished study, kept for reference |
| `prompt_analysis/` | The frozen prompt 1-lepton analysis: `1D_plots/`, `stack_plots/`, `regions/`, `datacards/`, `bkval/`, `cutflow/`, `truth/`, `ivf/` plus shared fillers at its root | Frozen reference (2020 to 2024) |
| `Signal_efficiency/`, `isolation_masspoint_check/`, `masspoint_2bd_test/`, `Branch_check/`, `json_sample_info/` | Small existing studies and inputs | Untouched |
| `utility/` | One-file ntuple/sample inspectors (self-contained) | Fine to use as-is |
| `Run_results_csv/` | CSV outputs of the old BR-pipeline generations | To be removed by hand later. `integral_test/` still reads it, so repoint those scripts to the `_extra` CSVs in `preselection_efficiency/` first |
| `legacy_archive/` | Superseded BR-pipeline generations (gen 1/3/4), generated job files, and the two obsolete condor MET-efficiency scans (`check_met_eff/`, `sample_stop_LL_check_met_eff/`) | Obsolete, delete when confident |
| `VarHandler.py` (top level) | Shared variable-computation class | Must stay here, it is imported by `preselection_efficiency/`, `CutFlow_study_LL/` and the prompt fillers |

## Which pipelines to update vs drop

- Update to the `preselection_efficiency/` way of working: `stack_plots_LL/` and `1D_plots_LL/` still plot signal from plain single samples (`SampleChain`). To show BR-weighted signal they should adopt `SampleChainSplittedBothBR.get2chain_simple()` and the three-term newComb combination (1-BR)*h(0.3) + BR*h(1.0) + h(1.0)_tail. `integral_test/` should switch its inputs from `Run_results_csv/info_test_new_comb_tight7_*` to `preselection_efficiency/info_test_new_comb_tight7_extra_*` before `Run_results_csv/` is deleted.
- Obsolete: everything in `legacy_archive/` (the gen-4 pair is fully contained in the `preselection_efficiency/` versions).
- Frozen reference: `prompt_analysis/`. Nothing in the LL analysis depends on it.

## Import/path fixes (applied July 2026)

The `sys.path` fixes were applied to `stack_plots_LL/`, `1D_plots_LL/`, `ctau_fit_study/` and all of `prompt_analysis/`. The convention, same as `preselection_efficiency/`, is: **run each script from inside its own folder**, because the relative `sys.path.append` entries resolve against the working directory. What was changed:

- Scripts one level down (`stack_plots_LL/`, `1D_plots_LL/`, `ctau_fit_study/`, `prompt_analysis/` root) now use `sys.path.append('../../')` to reach `Sample.*` and `Helper.*` in `test/`, and the `FillHistos*` fillers additionally append `'../'` before importing the top-level `VarHandler` (the append order matters: the `test/` path has to be there before `VarHandler` is imported, because `VarHandler` itself imports `Helper.VarCalc`).
- Scripts two levels down (`prompt_analysis/<subfolder>/`) use `sys.path.append('../../../')`. The two drivers importing the shared root filler (`1D_plots/1DPlot.py`, `stack_plots/StackHistMaker.py`) append `'../../../'`, `'../../'` and `'../'` before `from FillHistos import FillHistos`.
- The dead `from FillHistos_LL import FillHistos` import in `ctau_fit_study/1DPlot_LL_BR_weighted_bothBR.py` was commented out (the class was never used there and lives in `stack_plots_LL/` now).
- One pre-existing typo was fixed in passing: `prompt_analysis/cutflow/CutFlowHistScript.py` had `year = 2016PostVFP` without quotes, which was a syntax error.

Nothing else needed changing: drivers reference their workers by bare name and regenerate `parallelJobsubmit*.txt` / `parallel*.sh` in the working directory, and output paths come from the absolute `Sample.Dir.plotDir`. Verified by compiling every file and importing all the filler modules from their folders; the frozen prompt pipelines were not re-run beyond that.

Not fixed on purpose: everything under `legacy_archive/` still has the old flat-layout paths, since it is not meant to be run. Hardcoded input paths inside `ctau_fit_study/plot_tree_*` and `utility/` scripts were already stale before the reorg, so check them individually if you revive those.
