# Quick 1D histograms for the long-lived analysis

Two pipelines live here: a BR-weighted one for the displaced stop signal, and the older
single-chain one for data and background. Run everything **from inside this folder**, the
relative `sys.path` entries resolve against the working directory.

## Signal: `1DPlot_LL_signal.py` + `FillHistos_LL_signal.py`

The current tool for LL signal. It uses the same method as `../preselection_efficiency/`,
applied to the full ~28-variable set instead of just `stopCtau` and `MET`:

```bash
python 1DPlot_LL_signal.py --sample Sig_Splitted_500_490 --year 2018 --br 0.3
python 1DPlot_LL_signal.py --sample Sig_Splitted_500_490 --year 2018 --br 0.3 --nevents 2000   # quick look
python 1DPlot_LL_signal.py --sample Sig_Splitted_500_490 --year 2018 --br 0.3 --eletype Std    # electron collection
```

What it does:

- Loads the BR=0.3 and BR=1.0 chains with `SampleChainSplittedBothBR.get2chain_simple()`
  (keys `Sig_Splitted_<mStop>_<mLSP>_{0.3,1.0}` from the reworked FileLists), applies
  `passFilters()` plus `PreSelection()` from `TreeVarSel_LL`, and weights each event by
  `ReweightBRctau[BR*10-1]` for the requested `--br`.
- Combines the two chains as **(1-BR)*h(0.3) + BR*h(1.0) + tail**, with the bin errors set
  by hand as `sqrt(BR^2*e10^2 + (1-BR)^2*e03^2 + e_tail^2)`. The "tail" is anything with
  `stopCtau` (or `stopAntiCtau`) above 7 times the BR=0.3 sample ctau: discarded in the 0.3
  chain, kept as a separate unscaled histogram in the 1.0 chain. Both chains are compared
  against the **BR=0.3** ctau on purpose, so there is one cut point and no step in the
  combined ctau distribution.
- Weights follow `preselection_efficiency/`: `lumiscale = DataLumi * lumi_weight / 1000`
  (the reworked signal ntuples carry `lumi_weight`, not `weight`) and
  `MCcorr = MCWeight(...).getTotalWeight()` **without** the gen-filter efficiency, which is
  applied downstream at plotting time. `self.gfltreff` is still computed if you want it back.
- **No truth matching** — every event passing the selection is filled, which is what makes
  the yields directly comparable to the preselection-efficiency study.
- Tracks the decay-mode composition per event (`stopDecay`/`stopAntiDecay` with the 3.5
  threshold: 4bd+4bd, 4bd+2bd, 2bd+2bd) and appends one row per (mass point, BR) to
  `info_1DPlot_LL_signal_{03,10,combined}.csv` in this folder. As in
  `preselection_efficiency/` these are opened in append mode on purpose, so reruns add
  duplicate rows. The entries/integral columns are taken from a single fixed reference
  histogram (`MET`), not from whichever variable came last in the dictionary.

`--eletype` replaces the old `_std`/`_lowPt` script copies. It is passed straight to
`TreeVarSel`, and it picks the output location:

| `--eletype` | output directory | file suffix |
|---|---|---|
| `comb` (default) | `Plots/1DFiles_LL_signal/<year>/BR_<br>/` | none |
| `Std` | `Plots/1DFiles_LL_signal/<year>_std/BR_<br>/` | `_std` |
| `LowpT` | `Plots/1DFiles_LL_signal/<year>_lowPt/BR_<br>/` | `_lowPt` |

Note the output area is `1DFiles_LL_signal/`, **not** `1DFiles_LL/`: the
`preselection_efficiency/` grid sweep writes `1DFiles_LL/<year>/BR_<br>/` with identical
file names and would otherwise be clobbered.

## Data and background: `1DPlot_LL_old.py` (`_std`, `_lowPt`)

The previous generation, unchanged apart from the rename. Single chain via `SampleChain`,
`lumiscale = DataLumi/1000 * tr.weight`, `gfltreff` folded into `MCcorr`, and the
truth-matched-lepton gate of the `FillHistos_LL_TM_old*` fillers (leading lepton must have
`genPartFlav` in [1, 15]). Output goes to `Plots/1DFiles_LL/<year>[_std|_lowPt]/`.

```bash
python 1DPlot_LL_old.py --sample MET_Data --year 2018 --startfile 0 --nfiles 10 --nevents 10000
```

Use these for data and SM background; they do not do BR reweighting. The `_std` and
`_lowPt` copies differ only in the electron collection handed to `TreeVarSel` and in their
output directory.

## Overlay scripts

`plot_3_hist.py` overlays one variable for three mass points from the `1DFiles_LL` outputs,
and `plot_3_hist_different_e.py` overlays the same mass point across the comb/std/lowPt
outputs, which is the electron-collection comparison. Both still read the pre-BR paths under
`1DFiles_LL/`; point them at `1DFiles_LL_signal/<year>.../BR_<br>/` if you want them to read
the BR-weighted signal files.
