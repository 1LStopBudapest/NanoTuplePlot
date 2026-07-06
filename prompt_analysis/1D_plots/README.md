# Prompt 1D histograms

The prompt counterpart of the LL quick-look tool. `1DPlot.py` runs over one sample and draws essentially all analysis variables into `Plots/1DFiles/<year>/`. The event loop is `../FillHistos.py`. Typical call:

```bash
python 1DPlot.py --sample TTSingleLep_pow --year 2018 --startfile 0 --nfiles 10 --nevents 10000
```

`1DPlotScript.py` is the parallel driver that runs `1DPlot.py` for a list of samples via GNU `parallel` (config hardcoded at the top).

Frozen since around 2024, kept as reference. Imports were adjusted after the move: run the scripts from inside this folder.
