#!/bin/bash
#
# run.sh -- run one command inside the analysis environment, without having to
# source anything into your own shell.
#
#     ./run.sh python test_env.py
#     ./run.sh python 1DPlot_LL_BR_weighted_bothBR_newComb_peselection.py --sample ...
#
# You still need to be on EL7 first (`cmssw-el7`) when running interactively.
# Under condor that is handled by MY.SingularityImage in install_python.sub,
# which is the main reason this wrapper exists: a batch job has no shell to type
# `cmssw-el7` into, but it can be pointed at this script as its executable.
#
# The working directory is NOT changed -- run this from wherever your script
# expects to be, since the pipelines rely on relative sys.path.append entries.

set -euo pipefail

PREFIX="${STOP_ENV_PREFIX:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
export STOP_ENV_PREFIX="$PREFIX"

if [ $# -eq 0 ]; then
    echo "usage: $0 <command> [args...]" >&2
    echo "   eg: $0 python test_env.py" >&2
    exit 2
fi

source "$PREFIX/setup_env.sh"

exec "$@"
