#!/bin/bash
#
# probe_worker.sh -- executable for probe_worker.sub.
#
# Also the template for the real execute_condor_job_cutFlow.sh: it shows the
# three things that script is currently missing -- cd into the repo, set up the
# CMSSW environment, and pass ALL the arguments through.

echo "=== worker: $(hostname) in $PWD at $(date -u) ==="

# The job starts in condor's scratch dir. The analysis scripts resolve
# sys.path.append('../../') against the working directory, so we have to be in
# CutFlow_study_LL for anything to import. STOPANA_DIR comes from the .sub,
# expanded by condor_submit on the submit host.
if [ -z "${STOPANA_DIR:-}" ]; then
    echo "ERROR: STOPANA_DIR not set (the .sub should pass it)" >&2
    exit 1
fi
cd "$STOPANA_DIR" || { echo "ERROR: cannot cd to $STOPANA_DIR (kerberos token? EOS?)" >&2; exit 1; }
echo "=== now in $PWD ==="

# Python 2.7 + ROOT + numpy/matplotlib/pandas, all from CMSSW on /cvmfs.
# EL7 itself comes from MY.SingularityImage in the .sub -- do NOT call
# cmssw-el7 here, the pool already runs the job inside apptainer.
source ../set_python_lxplus/set_env.sh || { echo "ERROR: set_env.sh failed" >&2; exit 1; }

echo "=== running: python $@ ==="
python "$@"          # "$@", not $1 $2 $3 -- these command lines are 13 tokens
rc=$?
echo "=== done, exit $rc ==="
exit $rc
