#!/bin/bash
#
# install_venv.sh -- build the Python 2.7 virtualenv for this analysis, entirely
# inside this folder. Run it ONCE, from the terminal:
#
#     cmssw-el7                        # you enter the container yourself
#     cd .../NanoTuplePlot/venv_lxplus
#     bash install_venv.sh
#
# Idempotent: re-running it is a no-op once everything is in place.
#
# ROOT is NOT installed here -- it comes from CMSSW on /cvmfs. Only the four
# pinned libraries in requirements.txt are installed. See README.md.
#
# Run probe_lxplus.sh first if you have not: it reports which CMSSW releases
# exist, whether SCRAM_ARCH is needed, and what CMSSW already ships.

set -euo pipefail

# --- configuration ------------------------------------------------------------
# Overridable so a condor job can point at an absolute path (under condor,
# dirname "$0" is the worker's scratch dir, not this folder).
PREFIX="${STOP_ENV_PREFIX:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export STOP_ENV_PREFIX="$PREFIX"

VENV="$PREFIX/venv_folder"
CACHE="${STOP_ENV_CACHE:-$PREFIX/cache}"
SITE="$VENV/lib/python2.7/site-packages"
VIRTUALENV_PYZ_URL="https://bootstrap.pypa.io/virtualenv/2.7/virtualenv.pyz"
PIP_RETRIES=5

say()  { echo; echo "=== $* ==="; }
die()  { echo "ERROR: $*" >&2; exit 1; }

echo "install_venv.sh"
echo "    prefix : $PREFIX"
echo "    venv   : $VENV"
echo "    cache  : $CACHE"

mkdir -p "$CACHE"

# --- 1./2. EL7 check + CMSSW runtime ------------------------------------------
# setup_env.sh does both, plus the cache redirection. STOP_ENV_ALLOW_NO_VENV
# tells it not to complain that the venv it would activate does not exist yet.
say "1. CMSSW environment"
STOP_ENV_ALLOW_NO_VENV=1 source "$PREFIX/setup_env.sh" \
    || die "setup_env.sh failed -- see its message above"

# --- 3. check the interpreter before building on top of it --------------------
say "2. Interpreter check"
echo "    which python : $(command -v python)"
echo "    python -V    : $(python -V 2>&1)"

# Any 2.7.x is fine (2.7.5, 2.7.12 and 2.7.15 are ABI-compatible). Only two
# things actually matter, and both are fatal if wrong:
python -c 'import sys; assert sys.version_info[:2] == (2, 7), sys.version' \
    || die "not a Python 2.7 interpreter"

# UCS4 build? If this is UCS2, pip silently rejects every cp27mu manylinux1
# wheel and tries to compile numpy/scipy from source, which will fail.
python -c 'import sys; assert sys.maxunicode > 65535, "UCS2 build: cp27mu wheels cannot install"' \
    || die "UCS2 python -- cp27mu wheels will not install"
echo "    maxunicode   : $(python -c 'import sys; print(sys.maxunicode)')  (UCS4, wheels OK)"

# PyROOT must work BEFORE we build anything, otherwise the whole exercise is moot.
python -c 'import ROOT; print("    ROOT         : " + ROOT.gROOT.GetVersion())' \
    || die "'import ROOT' failed under the CMSSW environment"

# --- 4. create the virtualenv -------------------------------------------------
say "3. Virtualenv"
if [ -f "$VENV/bin/activate" ]; then
    echo "    already present, skipping"
else
    # python -m venv does not exist in 2.7. The pypa zipapp is a single file,
    # needs no pre-existing pip, and seeds the venv with the last py2-compatible
    # pip / setuptools / wheel (20.3.4 / 44.1.1) automatically.
    if [ ! -f "$CACHE/virtualenv.pyz" ]; then
        echo "    fetching virtualenv.pyz"
        curl -sSfL --retry 3 -o "$CACHE/virtualenv.pyz" "$VIRTUALENV_PYZ_URL" \
            || die "could not download $VIRTUALENV_PYZ_URL"
    fi
    # No --system-site-packages on purpose: PyROOT arrives via PYTHONPATH (which
    # a venv does not filter), so the flag buys nothing, while leaving it off
    # keeps pip's view clean and makes a missing dependency fail loudly.
    echo "    creating $VENV"
    python "$CACHE/virtualenv.pyz" "$VENV" || die "virtualenv creation failed"
fi

# --- 5. activate + prepend, then prove pip is the right pip -------------------
say "4. Activate"
set +u                      # see the note in setup_env.sh
source "$VENV/bin/activate"
set -u
export PYTHONPATH="$SITE${PYTHONPATH:+:$PYTHONPATH}"

# The most likely silent failure in this whole script: pip resolving to CMSSW's
# copy (because PYTHONPATH beats site-packages) and installing somewhere else.
pip_loc="$(python -c 'import pip, os; print(os.path.dirname(pip.__file__))')" \
    || die "the venv has no importable pip -- virtualenv.pyz seeding failed"
echo "    pip      : $(python -m pip --version 2>&1 | head -1)"
echo "    pip from : $pip_loc"
case "$pip_loc" in
    "$VENV"/*) echo "    OK -- pip is the venv's own" ;;
    *) die "pip resolves to $pip_loc, outside $VENV. The PYTHONPATH prepend did not take." ;;
esac

# --- 6. install the pins ------------------------------------------------------
say "5. Installing requirements"
installed=0
for try in $(seq 1 $PIP_RETRIES); do
    if python -m pip install -r "$PREFIX/requirements.txt"; then
        installed=1
        break
    fi
    echo "    attempt $try/$PIP_RETRIES failed, retrying..."
    sleep $((RANDOM % 20 + 5))
done
# The script this was adapted from fell through here and reported success with
# nothing installed. Do not do that.
[ "$installed" = "1" ] || die "pip install failed after $PIP_RETRIES attempts"

# --- 7. lock, scaffold, verify ------------------------------------------------
say "6. Freezing"
python -m pip freeze > "$PREFIX/requirements.lock.txt"
echo "    wrote requirements.lock.txt ($(wc -l < "$PREFIX/requirements.lock.txt") packages)"
echo "    commit that file -- it, not requirements.txt, is the reproducible set"

mkdir -p "$PREFIX/log" "$PREFIX/out" "$PREFIX/error"

say "7. Verifying"
python "$PREFIX/test_env.py" || die "test_env.py failed -- the environment is not usable"

# Reclaim ~200 MB by dropping the wheel cache. Left commented out because it
# makes any later reinstall much slower.
#python -m pip cache purge || true

cat <<EOF

==============================================================================
Done. In every new shell:

    cmssw-el7
    source $PREFIX/setup_env.sh

or, for a single command without sourcing:

    $PREFIX/run.sh python your_script.py

==============================================================================
EOF
