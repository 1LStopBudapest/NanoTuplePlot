# setup_env.sh -- SOURCE this (do not execute it) in every new shell.
#
#     cmssw-el7                                   # you run this yourself
#     source /path/to/venv_lxplus/setup_env.sh
#     cd ../preselection_efficiency && python plot_eff_grid.py
#
# What it does, in an order that matters:
#   1. checks you are on EL7 (i.e. inside cmssw-el7)
#   2. sets up the CMSSW runtime  -> gives Python 2.7 and PyROOT
#   3. activates the virtualenv   -> gives numpy/scipy/matplotlib/pandas
#   4. PREPENDS the venv site-packages to PYTHONPATH   <-- see README, load-bearing
#   5. redirects every cache into this folder so nothing is written to $HOME
#
# Deliberately no `set -e` / `set -u`: this is sourced into an interactive shell.

# --- must be sourced, not executed -------------------------------------------
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    echo "ERROR: source this script, do not execute it:" >&2
    echo "           source ${0}" >&2
    echo "       (to run a single command instead, use ./run.sh <cmd>)" >&2
    exit 1
fi

# --- configuration ------------------------------------------------------------
STOP_ENV_PREFIX="${STOP_ENV_PREFIX:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export STOP_ENV_PREFIX

# The CMSSW release supplying Python 2.7 + ROOT 6.14.
# The architecture appears only as a path component here, so there is no need to
# export SCRAM_ARCH -- scram reads the arch from the release's own .SCRAM/ dir.
# [probe_lxplus.sh section 4 confirms this release exists; section 5 confirms
#  whether the SCRAM_ARCH fallback below is needed.]
CMSSW_DIR="${CMSSW_DIR:-/cvmfs/cms.cern.ch/slc7_amd64_gcc700/cms/cmssw/CMSSW_10_6_30}"
# Fallback, only if `scram runtime` objects to an arch inherited from cmsset:
#export SCRAM_ARCH=slc7_amd64_gcc700

STOP_ENV_VENV="$STOP_ENV_PREFIX/venv_folder"
STOP_ENV_CACHE="${STOP_ENV_CACHE:-$STOP_ENV_PREFIX/cache}"
export STOP_ENV_VENV STOP_ENV_CACHE

# --- 1. EL7 check -------------------------------------------------------------
if ! grep -qs "release 7" /etc/redhat-release; then
    echo "ERROR: not on EL7 (this looks like $(cat /etc/redhat-release 2>/dev/null || uname -r))." >&2
    echo "       Enter the container first:   cmssw-el7" >&2
    echo "       then re-run:                 source ${BASH_SOURCE[0]}" >&2
    return 1
fi

# --- 2. CMSSW runtime: Python 2.7 + PyROOT ------------------------------------
if [ ! -d "$CMSSW_DIR" ]; then
    echo "ERROR: CMSSW release not found: $CMSSW_DIR" >&2
    echo "       Run probe_lxplus.sh to list what is available, then fix CMSSW_DIR" >&2
    echo "       at the top of setup_env.sh and install_venv.sh." >&2
    return 1
fi

# `|| true` on both: install_venv.sh sources this file under `set -e`, and a
# nonzero status here is benign -- the CMSSW_BASE check below is the real test.
source /cvmfs/cms.cern.ch/cmsset_default.sh >/dev/null 2>&1 || true
eval "$(cd "$CMSSW_DIR" && scramv1 runtime -sh 2>/dev/null)" || true
if [ -z "${CMSSW_BASE:-}${CMSSW_RELEASE_BASE:-}" ]; then
    echo "ERROR: 'scramv1 runtime -sh' produced no environment for $CMSSW_DIR" >&2
    echo "       See the SCRAM_ARCH / cmsrel fallbacks at the top of this file." >&2
    return 1
fi

# --- 3. + 4. virtualenv, then the PYTHONPATH prepend --------------------------
#
# The prepend is not cosmetic. sys.path is built as
#     [script dir] + $PYTHONPATH + stdlib + site-packages
# and site.py runs LAST, so anything on PYTHONPATH beats the venv's
# site-packages -- a virtualenv does not filter PYTHONPATH. CMSSW puts its own
# py2-numpy / py2-matplotlib / ... on PYTHONPATH, so without this prepend
# `import numpy` silently returns CMSSW's copy and the pins in requirements.txt
# are ignored. No error, just subtly different numbers.
#
# ROOT still imports fine: its $ROOTSYS/lib stays on PYTHONPATH, just later.
# This MUST come after `scram runtime`, which re-exports PYTHONPATH wholesale.
#
if [ -f "$STOP_ENV_VENV/bin/activate" ]; then
    # `set -u` breaks some activate scripts (unset PS1 / PYTHONHOME), and both
    # run.sh and install_venv.sh source us under it. Drop it just for this line.
    case $- in *u*) _stop_had_u=1; set +u ;; *) _stop_had_u=0 ;; esac
    source "$STOP_ENV_VENV/bin/activate"
    [ "$_stop_had_u" = "1" ] && set -u
    unset _stop_had_u
    STOP_ENV_SITE="$STOP_ENV_VENV/lib/python2.7/site-packages"
    export PYTHONPATH="$STOP_ENV_SITE${PYTHONPATH:+:$PYTHONPATH}"
elif [ "${STOP_ENV_ALLOW_NO_VENV:-0}" = "1" ]; then
    : # install_venv.sh sources us before the venv exists; that is expected
else
    echo "ERROR: no virtualenv at $STOP_ENV_VENV" >&2
    echo "       Create it first:   bash $STOP_ENV_PREFIX/install_venv.sh" >&2
    return 1
fi

# --- 5. keep every cache inside this folder, never in $HOME -------------------
export PIP_CACHE_DIR="$STOP_ENV_CACHE/pip"
export MPLCONFIGDIR="$STOP_ENV_CACHE/matplotlib"
export XDG_CACHE_HOME="$STOP_ENV_CACHE"
mkdir -p "$PIP_CACHE_DIR" "$MPLCONFIGDIR" 2>/dev/null || true

# Every plotting script in this repo already calls matplotlib.use('Agg'), but
# Signal_efficiency/signal_eff_BR_plot.py does not -- belt and braces.
export MPLBACKEND=Agg

# Do not spray .pyc files into the git tree (and the source dirs may be read-only).
export PYTHONDONTWRITEBYTECODE=1

# --- report -------------------------------------------------------------------
echo "stop analysis env ready"
echo "    python   : $(command -v python)  ($(python -V 2>&1))"
echo "    CMSSW    : $(basename "$CMSSW_DIR")"
echo "    venv     : $STOP_ENV_VENV"
echo "    caches   : $STOP_ENV_CACHE"
echo "    (verify with: python $STOP_ENV_PREFIX/test_env.py)"
