# venv_lxplus -- Python 2.7 + PyROOT environment for lxplus

A self-contained Python 2.7 environment for running this analysis on lxplus.
Everything lives inside this folder; nothing is written to `$HOME`.

ROOT is **not** installed here. It comes from CMSSW on `/cvmfs`, because PyROOT
is a compiled extension and has to match the interpreter it was built against.
Only the four pinned libraries in `requirements.txt` are installed.

## Quick start

```bash
# 0. once, to check what lxplus actually offers (paste the output to whoever
#    is maintaining these scripts if anything looks different)
cmssw-el7
bash probe_lxplus.sh 2>&1 | tee probe_output.txt

# 1. once, to build the environment (~5 min, ~500 MB in this folder)
bash install_venv.sh

# 2. in every new shell
cmssw-el7
source /path/to/NanoTuplePlot/venv_lxplus/setup_env.sh

# 3. run things as usual, from inside each pipeline's own folder
cd ../preselection_efficiency
python plot_eff_grid.py
```

For a single command without sourcing anything: `./run.sh python your_script.py`.
(`run.sh` does not change directory -- the pipelines rely on relative
`sys.path.append` entries resolving against the working directory, so run each
script from inside its own folder as usual.)

## Files

| File | What it is |
|---|---|
| `probe_lxplus.sh` | Read-only survey of the machine. Run first. Installs nothing. |
| `install_venv.sh` | Builds the virtualenv. Run once. Idempotent. |
| `setup_env.sh` | **Source** this per shell. CMSSW + venv + cache redirection. |
| `run.sh` | Thin wrapper: sets the env, runs one command. Used by condor. |
| `test_env.py` | Verifies the environment. Exits non-zero on failure. |
| `requirements.txt` | The four pins. |
| `requirements.lock.txt` | What pip actually resolved. Committed; the reproducible record. |
| `install_python.sub` | Condor smoke test -- proves the env works on a worker node. |

Generated and git-ignored: `venv_folder/`, `cache/`, `log/`, `out/`, `error/`.

## Why it is built this way

### The container and the interpreter

lxplus is AlmaLinux 9: no system Python 2, and no el8/el9 LCG view ships one.
`cmssw-el7` gets you an EL7 container, and CMSSW on `/cvmfs` supplies Python 2.7
plus ROOT 6.14 -- the same ROOT as the local (Higgs) machine.

The Python *micro* version does not matter: 2.7.5, 2.7.12 and 2.7.15 are
ABI-compatible, share a `cp27mu` wheel tag, and the pinned wheels run identically
on all of them. What matters is not mixing an interpreter with a foreign runtime.
`libPyROOT.so` links against `libpython2.7.so.1.0`, and `scram runtime` puts
CMSSW's libraries first on `LD_LIBRARY_PATH`; deliberately running
`/usr/bin/python` in that environment gives you the system interpreter with
CMSSW's libpython underneath it. So: run `scram runtime` first, then use whatever
`python` is on `PATH`. `install_venv.sh` does exactly that and never asserts a
specific micro version.

(`probe_lxplus.sh` section 8 tests whether `/usr/bin/python` can import ROOT
anyway. If it can, the distinction is moot.)

### The PYTHONPATH prepend -- do not remove it

`sys.path` is built as `[script dir] + $PYTHONPATH + stdlib + site-packages`, and
`site.py` runs **last**. So anything on `PYTHONPATH` beats a virtualenv's
`site-packages` -- a virtualenv does not filter `PYTHONPATH`.

`cmsenv` / `scram runtime` puts CMSSW's own `py2-numpy`, `py2-matplotlib` and
friends on `PYTHONPATH`. Activating the venv is therefore **not** enough on its
own: `import numpy` would return CMSSW's copy, the pins in `requirements.txt`
would be silently ignored, and you would get no error -- just slightly different
numbers than the local machine produces.

`setup_env.sh` fixes this by prepending the venv's `site-packages` to
`PYTHONPATH` *after* `scram runtime` (which re-exports `PYTHONPATH` wholesale, so
the order is load-bearing). `import ROOT` still works, because ROOT's
`$ROOTSYS/lib` stays on `PYTHONPATH`, just later in the list.

`test_env.py` prints each module's `__file__` and fails with `SHADOWED-BY:` if
any of the four resolves outside the venv. That check is the whole point of the
script -- there is no other way to tell a correct environment from a silently
wrong one.

Related: the venv is created **without** `--system-site-packages`. PyROOT arrives
via `PYTHONPATH` regardless, so the flag would buy nothing, while leaving it off
keeps pip's view clean and makes a missing dependency fail loudly.

### Nothing is written to `$HOME`

| Variable | Points at | Would otherwise write to |
|---|---|---|
| (virtualenv) | `venv_folder/` | `~/.local/lib/python2.7/site-packages` |
| `PIP_CACHE_DIR` | `cache/pip` | `~/.cache/pip` (~200 MB) |
| `MPLCONFIGDIR` | `cache/matplotlib` | `~/.cache/matplotlib` |
| `XDG_CACHE_HOME` | `cache/` | catch-all |
| `PYTHONDONTWRITEBYTECODE` | `1` | `.pyc` files in the repo tree |

Both `install_venv.sh` and `setup_env.sh` set these, so they apply when
installing *and* when merely running -- otherwise matplotlib would drop its font
cache in `$HOME` on every plot. To reclaim the ~200 MB pip cache afterwards,
uncomment the `pip cache purge` line at the end of `install_venv.sh`.

## Known limitation: the sample files are not on lxplus

The environment gets you a working `import ROOT`, but the event loops will then
fail on missing input. `Sample/FileList_LLStops_{2016,2017,2018}_reworked.py`
hardcode absolute local paths (`/mnt/newDisk/stop_samples_long_lived/...`) and
`SampleChainSplittedBothBR` uses them **raw** -- `Dir.userpath` is never applied,
so the lxplus branch of `Dir.py` does not help.

The reweighted files do exist at CERN, under
`/eos/cms/store/group/comm_luminosity/mleoncoe/...` (see `sample_reweighting/`).
Repointing them needs a decision -- either a `Dir.LLpath` prefix applied in the
FileLists, or an lxplus-specific FileList -- and has not been done yet.

The ROOT-free parts of the analysis work today: everything in
`preselection_efficiency/plot_*.py` reads CSVs and writes PNGs, needing only
matplotlib / pandas / numpy.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `not on EL7` | You skipped `cmssw-el7`. |
| `SHADOWED-BY: /cvmfs/...` | `PYTHONPATH` prepend lost -- something re-ran `cmsenv` after `setup_env.sh`. Re-source it. |
| `scramv1 runtime produced no environment` | Wrong `CMSSW_DIR`. Run `probe_lxplus.sh` section 4, then fix it at the top of `setup_env.sh`. There is also a commented `SCRAM_ARCH` fallback. |
| `UCS2 python` | Wrong interpreter; wheels cannot install. Check `which python` after `scram runtime`. |
| pip installs to the wrong place | `install_venv.sh` aborts on this deliberately; it means the prepend did not take. |
| condor job cannot read `/afs` | No kerberos token. `kinit` before `condor_submit` (`MY.SendCredential` is already set). |
| `Sample.Dir` raises `KeyError: 'USER'` | `Dir.py` reads `os.environ['USER']` unguarded and condor may not set it. The `.sub` passes `USER` through for this reason. |
