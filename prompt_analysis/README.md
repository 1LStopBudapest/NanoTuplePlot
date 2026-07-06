# Prompt 1-lepton stop analysis (frozen reference)

Everything in here belongs to the prompt compressed-stop search, not the long-lived one. None of it has been touched since roughly 2024 (some files since 2020), and the maintained prompt analysis lives elsewhere. This copy is kept as a working reference for how things were done: selections, datacard inputs, background validation, and the various plotting chains. Nothing in the LL analysis depends on this folder.

Each subfolder is one pipeline, and they all follow the same pattern: a `*Script*.py` driver with its configuration hardcoded at the top, which fans out worker jobs via GNU `parallel` and then calls a plotter. See the README in each subfolder.

The files at this level are the shared pieces used across the pipelines:

- `FillHistos.py`, the main event-loop histogram filler (uses `Helper.TreeVarSel`), imported by the 1D and stack pipelines.
- `FillHistos_Old.py`, an older version of the same, kept only for comparison.
- `VarHandler`, the variable-computation class these fillers import. Note it is still at the top of `NanoTuplePlot/`, not here, because the live LL pipelines import it too.
- `Compare.py` compares the keys/contents of two existing 1D-histogram ROOT files.
- `RatioPlot.py` makes unit-normalized shape comparisons between two samples (the old README already warned it may not work with current samples).
- `SoverB.py` computes S over sqrt(B) from existing histogram files.
- `SoftB.py` is a self-contained soft-b-tagging study.

Reminder: the analysis is blinded, so don't run the region or datacard pipelines over data.

The imports were adjusted after the move: run each script from inside its own subfolder (or from this folder for the root scripts), so the relative `sys.path` entries resolve and the drivers find their workers by bare name. Keep in mind these pipelines are frozen, so beyond the path fixes nothing was modernized or re-tested against current samples.
