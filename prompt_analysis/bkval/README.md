# Prompt background validation

Validation of the background estimate in two selection stages: `PromptBKVal1.py` and `PromptBKVal2.py` are the workers (both built on `Helper.TreeVarSel_BKVal` and `Binning_BKVal`), fanned out by `PromptBKValScript.py`, and the resulting stacks are drawn by `PromptBKValStackPlot.py` (pass it Val1 or Val2 to pick the stage). The `*JEC` trio is the same thing with `TreeVarSel_BKValJEC` for the JEC-shifted systematics.

Frozen since around 2024. Imports were adjusted after the move: run the scripts from inside this folder.
