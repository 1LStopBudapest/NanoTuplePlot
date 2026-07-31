# Sample reweighting (separate lxplus project)

This is a different project from the rest of NanoTuplePlot: it adds the `ReweightBRctau` branches to the input nanoAOD files, i.e. it produces the weights that the whole BR-reweighting machinery downstream relies on. It has been adapted to run on lxplus with condor and a newer Python, so nothing here follows the local Python 2.7 conventions.

Rough shape: `write_condor_jobs_weight*.py` generate the per-year condor job files (`jobs_2016/2017/2018`), the `reweightingBRandctau_*.py` scripts compute the width and ctau reweighting per event and write the new files, and `merge_job_outputs.py` / `merge_json.py` collect the outputs and the per-masspoint JSON summaries (`json_2016/2017/2018`). The `*.png` plots (widths, deltaM vs removed points, etc.) are diagnostics from those runs.

Do not run or modify this from the local machine; it is maintained separately on lxplus and only lives here as a checkout. This folder was deliberately left untouched by the July 2026 reorg.
