# Prompt cut-flow histograms

`CutFlowHistScript.py` drives `CutFlowHist.py`, which fills and plots the cut-flow per sample. Note it still imports the legacy `Helper.TreeVarSel_Old` selection, and the line that actually executes the parallel script is commented out in the driver. This one was already going stale before the reorg (last real work 2023). For the long-lived analysis there is a separate, newer cut-flow study in `../../CutFlow_study_LL/`.

Imports were adjusted after the move: run the scripts from inside this folder.
