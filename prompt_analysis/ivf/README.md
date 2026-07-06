# IVF (secondary vertex) studies

Studies of the inclusive vertex finder and displaced secondary vertices. Historically this was the stepping stone from the prompt analysis towards the long-lived one, though the code here still uses the prompt `Helper.TreeVarSel`. The chain is the usual one: `IVFPlotScript.py` fans out `IVFHistMaker.py` jobs (event loop in `FillHistos_IVF.py`, which also uses `Helper.IVFhelper`), and `IVFPlot.py` draws from the produced ROOT files.

Frozen since around 2023, the actual LL analysis has long since moved on. Imports were adjusted after the move: run the scripts from inside this folder.
