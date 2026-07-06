# Region histograms and region stacks

Two related chains for the analysis regions (SR1/SR2, CR1/CR2, etc., defined in `Helper/TreeVarSel.py`):

- `MakeRegionHistScripy.py` drives `RegionHistMaker.py`: batch production of region histogram ROOT files for the whole signal grid, the SM backgrounds, or data (`--sample Signal` or `Other`, region chosen with `--region`). No plotting, just the files that feed limits and tables. The analysis is blinded, so don't run this over data.
- `StackPlotScript_Region.py` drives `RegionPlot.py` and then `StackPlot_Region.py`: the per-region data/MC stack plots.

`RegionpTplot.py` is a standalone extra that plots lepton pT inside a region. It isn't called by either driver.

Frozen since around 2024. Imports were adjusted after the move: run the scripts from inside this folder.
