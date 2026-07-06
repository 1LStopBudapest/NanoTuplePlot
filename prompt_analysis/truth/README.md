# Gen-truth studies

Generator-level truth studies for the prompt analysis. `TruePlot.py` is the driver/plotter and `TrueFill.py` its event-loop filler, built on `Helper.TreeVarSel_true` and `Helper.IVFhelper`. `TrueTest.py` is a scratch script that mixes the reco (`TreeVarSel`) and truth (`TreeVarSel_true`) selections for cross-checks. It was never wired into a driver.

Old (2022-era) and frozen, kept as reference. Imports were adjusted after the move: run the scripts from inside this folder.
