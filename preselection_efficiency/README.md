# Preselection efficiency and expected signal yields

The canonical, active study of the long-lived analysis. It measures the preselection efficiency and the expected signal yield across the (m_stop, m_X0) grid as a function of the stop to 4-body branching ratio (BR). It is used to pick viable mass points and BRs, validate the BR-reweighting scheme, cross-check against the prompt analysis, and design a better preselection for the displaced search.

How the pipeline runs, always from inside this folder:

1. `write_test_commands.py` reads `../json_sample_info/summed_2018_reworked.json` (events per mass point per BR), drops mass points with deltaM above 50 GeV, degenerate masses or too few events, and writes `execute_test.sh` with one job per mass point and BR from 0.1 to 1.0.
2. Each job runs `1DPlot_LL_BR_weighted_bothBR_newComb_peselection.py`, which loads the BR=0.3 and BR=1.0 chains through `SampleChainSplittedBothBR.get2chain_simple()` (sample keys like `Sig_Splitted_500_490_0.3` from the reworked FileLists).
3. `FillHistos_LL_bothBR_newComb_preselection.py` applies the real reco selection (`passFilters()` plus `PreSelection()` with 'comb' electrons), combines the two samples as (1-BR)*h(0.3) + BR*h(1.0) + tail with manual error propagation, tracks the decay-mode composition per event (4bd+4bd, 4bd+2bd, 2bd+2bd, from `stopDecay`/`stopAntiDecay` with the 3.5 threshold), and appends one row per (mass point, BR) to the `info_test_new_comb_tight7_extra_{03,10,combined}.csv` files. The "tail" is anything with stopCtau over 7 times the BR=0.3 sample ctau: rejected in the 0.3 chain, kept as a separate unscaled histogram in the 1.0 chain.
4. The `plot_*` scripts read those CSVs together with the NNLO+NNLL cross sections (`stops_13TeV.py`, converted pb to fb) and the gen-filter efficiencies (`AuxFiles/csv_appended_filterEff.csv`) and draw the 2D grid PNGs. Expected yields use the per-decay-mode efficiencies: N = lumi * sigma * (BR^2 * eff44 * w44 + 2 BR (1-BR) * eff42 * w42 + (1-BR)^2 * eff22 * w22) for each source sample.

Which files are current: the `*_correct.py` plotting scripts and the `_extra` CSVs. The `noSel` variants are the same thing without the preselection (for the efficiency denominator), and the non-`extra`, non-`_correct` files are older iterations kept for reference. Filename tags: `newComb` is the current combination method, `tight7` the ctau-ratio tail threshold of 7.

Two practical warnings. The CSVs are opened in append mode on purpose, so reruns add duplicate rows (useful for debugging, don't "fix" it). And grid sweeps over all mass points run for days in a screen session; check `ps`/`screen -ls` before launching anything here, because jobs write to the same CSVs and the same `Plots/1DFiles_LL/<year>/BR_*` outputs.
