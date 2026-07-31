# Branch checks

Small standalone inspectors for the post-processed nanoAOD files: list which branches exist, count entries, and compare the content or structure of two files. Handy when a new batch of samples arrives and you want to confirm the post-processing produced what you expect (the `*Priya*` variants were made while debugging files exchanged with a colleague).

- `checkBranches.py`, `checkBranches_onefile.py`, `checkBranchesAndCounts.py` list branches (and counts) for a file or set of files.
- `compareTwoFIles.py` and `compareStructureTwoFiles.py` diff the content and the tree structure of two files.
- `checkEventBranch.py` inspects a single branch in detail.
- `checkIntMasspoints.py` checks which mass points are present.

All of them have their input paths hardcoded near the top; edit and run. No `Sample`/`Helper` imports, so they work from anywhere.
