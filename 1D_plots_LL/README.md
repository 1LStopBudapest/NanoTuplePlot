# Quick 1D histograms for the long-lived analysis

The everyday "plot one sample" tool. `1DPlot_LL.py` loops over a single sample (data or MC) and produces a ROOT file plus pdf/png of around 27 variables under `Plots/1DFiles_LL/<year>/`. Typical usage for a quick look:

```bash
python 1DPlot_LL.py --sample MET_Data --year 2016PostVFP --startfile 0 --nfiles 10 --nevents 10000
```

The event loop lives in the `FillHistos_LL_TM*.py` fillers (applies `passFilters()` plus `PreSelection()` from `TreeVarSel_LL`). As with the stack plots, the base version uses the combined electron collection while `_std` and `_lowPt` restrict to a single collection and write to `1DFiles_LL_std` and `1DFiles_LL_lowPt`.

The two small overlay scripts belong to the same family: `plot_3_hist.py` overlays one variable for three mass points from the `1DFiles_LL` outputs, and `plot_3_hist_different_e.py` overlays the same mass point across the comb/std/lowPt outputs, which is the electron-collection comparison.

Status: active as a generic tool. If BR-weighted signal shapes are ever needed here, this would adopt the `SampleChainSplittedBothBR` plus newComb combination from `preselection_efficiency/`.

The imports were adjusted after the move: run the scripts from inside this folder (same convention as `preselection_efficiency/`), so the relative `sys.path` entries resolve.
