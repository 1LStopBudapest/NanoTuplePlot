# Prompt data/MC stack plots

The inclusive data/MC stack pipeline for the prompt analysis. `StackPlotScript.py` is the driver: it writes the job list, runs `StackHistMaker.py` per file chunk through GNU `parallel` (the worker imports `../FillHistos.py` for the event loop), hadds the per-process outputs under `Plots/StackFiles/`, and finishes by calling `StackPlot.py` to draw the stacked histograms.

Frozen since around 2024. The LL equivalent lives in `../../stack_plots_LL/`. Imports were adjusted after the move: run the scripts from inside this folder.
