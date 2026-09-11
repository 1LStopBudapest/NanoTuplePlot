# set_python_lxplus -- Python 2.7 + ROOT environment for lxplus

**Nothing is installed here.** CMSSW on `/cvmfs` already provides everything this
analysis needs, so this folder is one activation script plus two diagnostics.

## Quick start

```bash
cmssw-el7                                          # enter the EL7 container
source /path/to/NanoTuplePlot/set_python_lxplus/set_env.sh
cd ../preselection_efficiency && python plot_eff_grid.py
```

That is the whole setup. Run each script from inside its own folder, as on the
local machine -- the pipelines rely on relative `sys.path.append` entries
resolving against the working directory.

To check the environment at any point: `python set_python_lxplus/test_env.py`.

## Why nothing needs installing

`probe_lxplus.sh` measured `CMSSW_10_6_50` (`slc7_amd64_gcc700`) on 2026-09-11:

| Package | CMSSW_10_6_50 | Local (Higgs) machine |
|---|---|---|
| Python | 2.7.14+ | 2.7.12 |
| ROOT | 6.14/09 | 6.14/04 |
| numpy | **1.16.2** | 1.16.2 -- identical |
| pandas | **0.24.2** | 0.24.2 -- identical |
| matplotlib | 2.2.4 | 2.2.2 |
| scipy | 1.2.1 | 1.2.3 |
| tabulate | not present | only `Signal_efficiency/`, `legacy_archive/` |
| six, cycler, pyparsing, kiwisolver, dateutil, pytz | all present | |

The complete third-party dependency set of this repo, from grepping all 232
`.py` files, is `ROOT`, `numpy`, `matplotlib`, `pandas`, `scipy`, `tabulate` and
a `pathlib` backport. The active LL pipelines (`preselection_efficiency/`,
`CutFlow_study_LL/`, `stack_plots_LL/`, `1D_plots_LL/`) use only the first four
-- all supplied by CMSSW, with the two most important at exactly the local
versions.

If you ever need `tabulate` or another package CMSSW lacks, no virtualenv is
required:

```bash
source set_env.sh
export PYTHONUSERBASE="$STOP_ENV_PREFIX/pylibs"   # keeps it in this folder,
python -m pip install --user tabulate             # not in ~/.local
```

You would need that same `PYTHONUSERBASE` line in every later shell, so if this
ever becomes more than one stray package, add it to `set_env.sh` and put
`pylibs/` in `.gitignore`.

## Two things worth knowing

### Use the python `scram runtime` gives you

Do not reach past it to `/usr/bin/python`. The container ships Python 2.7.5, but
under CMSSW's `LD_LIBRARY_PATH` that binary loads CMSSW's `libpython2.7`
(2.7.14+) and then cannot find its own stdlib:

```
Could not find platform independent libraries <prefix>
```

The mismatch is interpreter vs runtime, not one Python version against another
-- 2.7.5, 2.7.12 and 2.7.14 are otherwise ABI-compatible, so the version digits
themselves do not matter. `set_env.sh` puts the right one on `PATH`, and
`test_env.py` warns if `sys.executable` is not under `/cvmfs`.

### No `SCRAM_ARCH` export is needed

`cmsset_default.sh` leaves `SCRAM_ARCH` at `slc7_amd64_gcc12`, yet
`scramv1 runtime -sh` still resolves correctly from the read-only release area,
because it reads the architecture from the release's own `.SCRAM/` directory.
Verified both with and without the export.

## What else `set_env.sh` sets

Almost nothing. Caches are left at their defaults -- with nothing installed, the
only one ever written is matplotlib's font list, a few hundred KB in
`~/.cache/matplotlib`, created once and then reused. `.pyc` files need no
handling either: `*.pyc` is already in the `.gitignore` of all three repos
(`NanoTuplePlot`, `Sample`, `Helper`), none are tracked, and they never appear
in `git status`.

The one export that remains is `MPLBACKEND=Agg`. Every plotting script calls
`matplotlib.use('Agg')` itself except `Signal_efficiency/signal_eff_BR_plot.py`,
which would otherwise try to open a window on a node with no display.

## Files

| File | What it is |
|---|---|
| `set_env.sh` | **Source** this per shell. The only thing you normally need. |
| `test_env.py` | Verifies the environment. Exits non-zero on failure. |
| `probe_lxplus.sh` | Read-only survey of the machine. Re-run it if CMSSW moves or versions change. |

## Known limitation: the sample files are not on lxplus

`import ROOT` works, but the event loops will then fail on missing input.
`Sample/FileList_LLStops_{2016,2017,2018}_reworked.py` hardcode absolute local
paths (`/mnt/newDisk/stop_samples_long_lived/...`) and
`SampleChainSplittedBothBR` uses them **raw** -- `Dir.userpath` is never applied,
so the lxplus branch of `Dir.py` does not help.

The reweighted files do exist at CERN, under
`/eos/cms/store/group/comm_luminosity/mleoncoe/...` (see `sample_reweighting/`).
Repointing them needs a decision -- a `Dir.LLpath` prefix applied in the
FileLists, or an lxplus-specific FileList -- and has not been done yet.

The ROOT-free parts work today: everything in
`preselection_efficiency/plot_*.py` reads CSVs and writes PNGs.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `not on EL7` | You skipped `cmssw-el7`. |
| `Could not find platform independent libraries` | You used `/usr/bin/python` instead of the one on `PATH`. |
| `scramv1 runtime produced no environment` | Wrong `CMSSW_DIR`. Run `probe_lxplus.sh` (section 4) and fix it at the top of `set_env.sh`. |
| plots try to open a window / crash with no display | `set_env.sh` was not sourced, so `MPLBACKEND` is unset. |
| `Sample.Dir raises KeyError: 'USER'` | `Dir.py` reads `os.environ['USER']` unguarded and something cleared it. |
