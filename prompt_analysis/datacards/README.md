# Datacard input histograms

Produces the histograms that go into the combine datacards, including systematics.

`CountDCHistScript.py` is the driver. Depending on its `dc` setting it fans out either `CountDCHist.py` (cut and count, the big one, rates plus all the systematic variations) or `ShapeDCHist.py` (shape analysis variant). The JEC/JER up/down systematics are handled by the parallel chain `CountDCHistJECScript.py` driving `CountDCHistJEC.py`, which differs mainly by using `Helper.TreeVarSel_JEC` (JEC-shifted object selection) instead of the nominal `TreeVarSel`.

Blinded analysis, don't run over data. Frozen since around 2024. Imports were adjusted after the move: run the scripts from inside this folder.
