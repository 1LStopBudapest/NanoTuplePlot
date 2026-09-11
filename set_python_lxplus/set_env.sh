# set_env.sh -- SOURCE this (do not execute it) in every new shell on lxplus.
#
#     cmssw-el7                                   # you run this yourself
#     source /path/to/set_python_lxplus/set_env.sh
#     cd ../preselection_efficiency && python plot_eff_grid.py
#
# Nothing is installed, here or anywhere. CMSSW on /cvmfs already provides
# everything this analysis needs -- Python 2.7, ROOT 6.14, numpy, matplotlib,
# pandas and scipy -- so all this script does is put that environment on PATH.
# See README.md for the measurements behind that claim.
#
# Deliberately no `set -e` / `set -u`: this is sourced into an interactive shell.

# --- must be sourced, not executed -------------------------------------------
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    echo "ERROR: source this script, do not execute it:" >&2
    echo "           source ${0}" >&2
    exit 1
fi

STOP_ENV_PREFIX="${STOP_ENV_PREFIX:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export STOP_ENV_PREFIX

# The CMSSW release supplying Python 2.7 + ROOT + the python libraries.
# 10_6_50 specifically, because that is the one probe_lxplus.sh measured:
# numpy 1.16.2 and pandas 0.24.2 (identical to the local machine), matplotlib
# 2.2.4, scipy 1.2.1, ROOT 6.14/09. Any other 10_6_X should be close, but if you
# change this, re-run probe_lxplus.sh and check section 7 again.
#
# No SCRAM_ARCH export is needed: scram reads the architecture from the
# release's own .SCRAM/ directory. (Verified -- cmsset_default.sh leaves
# SCRAM_ARCH at slc7_amd64_gcc12 and `scramv1 runtime` still resolves correctly.)
CMSSW_DIR="${CMSSW_DIR:-/cvmfs/cms.cern.ch/slc7_amd64_gcc700/cms/cmssw/CMSSW_10_6_50}"

# --- 1. EL7 check -------------------------------------------------------------
if ! grep -qs "release 7" /etc/redhat-release; then
    echo "ERROR: not on EL7 (this looks like $(cat /etc/redhat-release 2>/dev/null || uname -r))." >&2
    echo "       Enter the container first:   cmssw-el7" >&2
    echo "       then re-run:                 source ${BASH_SOURCE[0]}" >&2
    return 1
fi

# --- 2. CMSSW runtime ---------------------------------------------------------
if [ ! -d "$CMSSW_DIR" ]; then
    echo "ERROR: CMSSW release not found: $CMSSW_DIR" >&2
    echo "       Run probe_lxplus.sh (section 4) to list what is available," >&2
    echo "       then fix CMSSW_DIR at the top of this file." >&2
    return 1
fi

source /cvmfs/cms.cern.ch/cmsset_default.sh >/dev/null 2>&1 || true
eval "$(cd "$CMSSW_DIR" && scramv1 runtime -sh 2>/dev/null)" || true
if [ -z "${CMSSW_BASE:-}${CMSSW_RELEASE_BASE:-}" ]; then
    echo "ERROR: 'scramv1 runtime -sh' produced no environment for $CMSSW_DIR" >&2
    return 1
fi

# Use the python that scram just put on PATH -- do not reach past it to
# /usr/bin/python. That binary is 2.7.5, but under CMSSW's LD_LIBRARY_PATH it
# loads CMSSW's libpython2.7 (2.7.14+) and then fails to find its own stdlib:
#     Could not find platform independent libraries <prefix>
# The mismatch is interpreter vs runtime, not one python version vs another.

# --- 3. one convenience -------------------------------------------------------
# Caches are left at their defaults (~/.cache): the only one that gets written
# is matplotlib's font cache, a few hundred KB written once and then reused.
# .pyc files are already gitignored in all three repos, so they need no handling.

# Every plotting script here calls matplotlib.use('Agg') itself, except
# Signal_efficiency/signal_eff_BR_plot.py -- this keeps that one from failing
# on a node with no display.
export MPLBACKEND=Agg

echo "stop analysis env ready  (CMSSW $(basename "$CMSSW_DIR"), nothing installed)"
echo "    python : $(command -v python)"
echo "    verify : python $STOP_ENV_PREFIX/test_env.py"
