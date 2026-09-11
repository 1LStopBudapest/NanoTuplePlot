#!/bin/bash
#
# probe_lxplus.sh -- read-only survey of what is available on lxplus for building
# the Python 2.7 + PyROOT environment in this folder.
#
# Run it FIRST, inside the container:
#
#     cmssw-el7
#     bash probe_lxplus.sh 2>&1 | tee probe_output.txt
#
# It installs nothing, writes nothing outside /tmp, and is safe to re-run.
# Paste the whole output back so the pinned values in install_venv.sh and
# requirements.txt can be set from measurements instead of guesses.
#
# Optional override, if you want to probe a specific release:
#     CMSSW_DIR=/cvmfs/cms.cern.ch/slc7_amd64_gcc700/cms/cmssw/CMSSW_10_6_30 bash probe_lxplus.sh

# NOTE: deliberately no `set -e`. A probe that dies halfway is useless -- every
# section is allowed to fail and report the failure.
set +e

CMS_BASE=/cvmfs/cms.cern.ch
CMSSET="$CMS_BASE/cmsset_default.sh"
ARCH_GUESS=slc7_amd64_gcc700
RELEASE_GLOB='CMSSW_10_6_*'

hdr() {
    echo
    echo "=============================================================================="
    echo "== $*"
    echo "=============================================================================="
}

note() { echo "    -> $*"; }

echo "##############################################################################"
echo "## probe_lxplus.sh   $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "##############################################################################"

# -----------------------------------------------------------------------------
hdr "1. Host / container"
# -----------------------------------------------------------------------------
echo "hostname        : $(hostname -f 2>/dev/null || hostname)"
echo "uname -r        : $(uname -r)"
echo "uname -m        : $(uname -m)"
echo -n "redhat-release  : "; cat /etc/redhat-release 2>/dev/null || echo "(none)"
echo "USER            : ${USER:-<unset>}"
echo "PWD             : $PWD"
echo "APPTAINER_CONTAINER  : ${APPTAINER_CONTAINER:-<unset>}"
echo "SINGULARITY_CONTAINER: ${SINGULARITY_CONTAINER:-<unset>}"

IN_EL7=no
if grep -qs "release 7" /etc/redhat-release; then
    IN_EL7=yes
fi
echo "on EL7          : $IN_EL7"
if [ "$IN_EL7" != "yes" ]; then
    note "NOT on EL7. Sections 5-8 will be skipped or will fail."
    note "Re-run inside the container:  cmssw-el7   then   bash probe_lxplus.sh"
fi

# -----------------------------------------------------------------------------
hdr "2. Bare python (before any CMSSW setup)"
# -----------------------------------------------------------------------------
for py in python python2 python2.7 /usr/bin/python /usr/bin/python2 python3; do
    p="$(command -v "$py" 2>/dev/null)"
    if [ -n "$p" ]; then
        printf '%-22s %-28s %s\n' "$py" "$p" "$("$p" -V 2>&1 | head -1)"
    else
        printf '%-22s %s\n' "$py" "(not found)"
    fi
done
echo
echo -n "maxunicode of 'python' : "
python -c 'import sys; print(sys.maxunicode)' 2>&1 | head -1
note "1114111 = UCS4 = cp27mu wheels OK.  65535 = UCS2 = wheels will NOT install."

# -----------------------------------------------------------------------------
hdr "3. CVMFS"
# -----------------------------------------------------------------------------
for d in /cvmfs /cvmfs/cms.cern.ch /cvmfs/sft.cern.ch /cvmfs/unpacked.cern.ch; do
    if [ -d "$d" ]; then echo "OK      $d"; else echo "MISSING $d"; fi
done
echo
echo -n "cmsset_default.sh : "
[ -f "$CMSSET" ] && echo "present ($CMSSET)" || echo "MISSING"
echo
echo "architectures under $CMS_BASE :"
ls -1 "$CMS_BASE" 2>/dev/null | grep -E '^(slc|el)[0-9]' | sed 's/^/    /' || echo "    (none listed)"

# -----------------------------------------------------------------------------
hdr "4. Available CMSSW 10_6 releases"
# -----------------------------------------------------------------------------
echo "under $ARCH_GUESS :"
ls -1d "$CMS_BASE/$ARCH_GUESS/cms/cmssw/"$RELEASE_GLOB 2>/dev/null \
    | xargs -r -n1 basename | sort -V | sed 's/^/    /' \
    || echo "    (none found)"

# Pick the release to probe with: explicit override, else highest 10_6_*.
if [ -z "${CMSSW_DIR:-}" ]; then
    CMSSW_DIR="$(ls -1d "$CMS_BASE/$ARCH_GUESS/cms/cmssw/"$RELEASE_GLOB 2>/dev/null \
                 | sort -V | tail -1)"
fi
echo
echo "release chosen for the rest of this probe:"
echo "    ${CMSSW_DIR:-<none found>}"
if [ -n "$CMSSW_DIR" ] && [ -d "$CMSSW_DIR/.SCRAM" ]; then
    echo
    echo "architectures declared in its .SCRAM/ :"
    ls -1 "$CMSSW_DIR/.SCRAM" 2>/dev/null | grep -E '^(slc|el)[0-9]' | sed 's/^/    /'
    note "scram reads the arch from here, which is why no SCRAM_ARCH export should be needed."
fi

if [ -z "$CMSSW_DIR" ]; then
    note "No CMSSW_10_6_* release found -- skipping sections 5-8."
fi

# -----------------------------------------------------------------------------
hdr "5. Does 'scramv1 runtime -sh' work from the read-only release area?"
# -----------------------------------------------------------------------------
if [ -n "$CMSSW_DIR" ] && [ -f "$CMSSET" ]; then

    echo "--- 5a: WITHOUT exporting SCRAM_ARCH ---"
    (
        source "$CMSSET" >/dev/null 2>&1
        echo "    SCRAM_ARCH after cmsset : ${SCRAM_ARCH:-<unset>}"
        out="$(cd "$CMSSW_DIR" && scramv1 runtime -sh 2>&1)"
        rc=$?
        if [ $rc -eq 0 ] && echo "$out" | grep -q 'export'; then
            echo "    RESULT: SUCCESS ($(echo "$out" | grep -c export) export lines)"
        else
            echo "    RESULT: FAILED (rc=$rc)"
            echo "$out" | head -10 | sed 's/^/      | /'
        fi
    )

    echo
    echo "--- 5b: WITH SCRAM_ARCH=$ARCH_GUESS exported ---"
    (
        export SCRAM_ARCH="$ARCH_GUESS"
        source "$CMSSET" >/dev/null 2>&1
        out="$(cd "$CMSSW_DIR" && scramv1 runtime -sh 2>&1)"
        rc=$?
        if [ $rc -eq 0 ] && echo "$out" | grep -q 'export'; then
            echo "    RESULT: SUCCESS ($(echo "$out" | grep -c export) export lines)"
        else
            echo "    RESULT: FAILED (rc=$rc)"
            echo "$out" | head -10 | sed 's/^/      | /'
        fi
    )
    note "If 5a succeeds, install_venv.sh needs no SCRAM_ARCH export."
    note "If only 5b succeeds, uncomment the SCRAM_ARCH line in install_venv.sh."
    note "If both fail, we fall back to a cmsrel dev area."
else
    echo "SKIPPED (no release or no cmsset_default.sh)"
fi

# -----------------------------------------------------------------------------
hdr "6. What the CMSSW environment provides"
# -----------------------------------------------------------------------------
if [ -n "$CMSSW_DIR" ] && [ -f "$CMSSET" ]; then
(
    source "$CMSSET" >/dev/null 2>&1
    eval "$(cd "$CMSSW_DIR" && scramv1 runtime -sh 2>/dev/null)"

    echo "which python    : $(command -v python)"
    echo "python -V       : $(python -V 2>&1)"
    echo "maxunicode      : $(python -c 'import sys; print(sys.maxunicode)' 2>&1)"
    echo
    echo "ROOT:"
    python - <<'PYEOF' 2>&1 | sed 's/^/    /'
try:
    import ROOT
    print("version  : %s" % ROOT.gROOT.GetVersion())
    print("__file__ : %s" % ROOT.__file__)
except Exception as e:
    print("IMPORT FAILED: %r" % (e,))
PYEOF
    echo
    echo "PYTHONPATH entries:"
    if [ -n "${PYTHONPATH:-}" ]; then
        echo "$PYTHONPATH" | tr ':' '\n' | sed 's/^/    /'
    else
        echo "    <empty>"
    fi
    echo
    echo "LD_LIBRARY_PATH entry count: $(echo "${LD_LIBRARY_PATH:-}" | tr ':' '\n' | grep -c .)"
)
else
    echo "SKIPPED"
fi

# -----------------------------------------------------------------------------
hdr "7. Which libraries CMSSW already ships  [MOST IMPORTANT SECTION]"
# -----------------------------------------------------------------------------
if [ -n "$CMSSW_DIR" ] && [ -f "$CMSSET" ]; then
(
    source "$CMSSET" >/dev/null 2>&1
    eval "$(cd "$CMSSW_DIR" && scramv1 runtime -sh 2>/dev/null)"
    python - <<'PYEOF' 2>&1 | sed 's/^/    /'
mods = ["numpy", "scipy", "matplotlib", "pandas", "tabulate", "six", "cycler",
        "pyparsing", "kiwisolver", "dateutil", "pytz", "pip", "setuptools",
        "wheel", "virtualenv"]
for m in mods:
    try:
        mod = __import__(m)
        ver = getattr(mod, "__version__", "?")
        print("%-12s %-10s %s" % (m, ver, getattr(mod, "__file__", "?")))
    except Exception:
        print("%-12s %s" % (m, "NOT PRESENT"))
PYEOF
)
    note "Anything listed with a /cvmfs/ path is on PYTHONPATH and WILL shadow the venv"
    note "unless install_venv.sh/setup_env.sh prepend the venv site-packages."
    note "Anything 'NOT PRESENT' must come from requirements.txt."
else
    echo "SKIPPED"
fi

# -----------------------------------------------------------------------------
hdr "8. Can the container's own python import CMSSW's ROOT?"
# -----------------------------------------------------------------------------
if [ -n "$CMSSW_DIR" ] && [ -f "$CMSSET" ] && [ -x /usr/bin/python ]; then
(
    source "$CMSSET" >/dev/null 2>&1
    eval "$(cd "$CMSSW_DIR" && scramv1 runtime -sh 2>/dev/null)"
    echo "    /usr/bin/python -V : $(/usr/bin/python -V 2>&1)"
    echo -n "    import ROOT        : "
    out="$(/usr/bin/python -c 'import ROOT; print("OK  " + ROOT.gROOT.GetVersion())' 2>&1)"
    rc=$?
    echo "$out" | head -3
    echo "    (exit code $rc -- 139 would mean a segfault, i.e. libpython mismatch)"
)
    note "If this works, either interpreter is viable and the choice does not matter."
    note "If it segfaults or ImportErrors, the venv must be built from CMSSW's python."
else
    echo "SKIPPED"
fi

# -----------------------------------------------------------------------------
hdr "9. Alternative base: LCG python2 views (reference only)"
# -----------------------------------------------------------------------------
if [ -d /cvmfs/sft.cern.ch/lcg/views ]; then
    echo "LCG views matching python2:"
    ls -1 /cvmfs/sft.cern.ch/lcg/views 2>/dev/null \
        | grep -i 'python2' | sed 's/^/    /' | head -20
    echo
    echo "platforms under LCG_97python2 (if present):"
    ls -1 /cvmfs/sft.cern.ch/lcg/views/LCG_97python2 2>/dev/null | sed 's/^/    /' \
        || echo "    (not present)"
else
    echo "/cvmfs/sft.cern.ch/lcg/views not mounted"
fi

# -----------------------------------------------------------------------------
hdr "10. Network reachability (needed for pip)"
# -----------------------------------------------------------------------------
if command -v curl >/dev/null 2>&1; then
    for url in https://pypi.org/simple/ \
               https://files.pythonhosted.org/ \
               https://bootstrap.pypa.io/virtualenv/2.7/virtualenv.pyz ; do
        code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 -I "$url" 2>&1)"
        printf '    %-62s HTTP %s\n' "$url" "$code"
    done
    note "Any 200/301/302 is fine. 000 means no route / TLS failure."
else
    echo "curl not found"
    command -v wget >/dev/null 2>&1 && echo "(wget is available as a fallback)"
fi

# -----------------------------------------------------------------------------
hdr "11. Storage for this folder (~500 MB needed)"
# -----------------------------------------------------------------------------
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "folder          : $HERE"
echo "filesystem type : $(stat -f -c %T "$HERE" 2>/dev/null || echo '?')"
echo
echo "df -h:"
df -h "$HERE" 2>&1 | sed 's/^/    /'
echo
if command -v fs >/dev/null 2>&1; then
    echo "fs quota (AFS):"
    fs quota "$HERE" 2>&1 | sed 's/^/    /'
    fs lq "$HERE" 2>&1 | sed 's/^/    /'
else
    echo "(no AFS 'fs' command -- not on AFS, or tools absent in the container)"
fi

# -----------------------------------------------------------------------------
hdr "12. Pre-existing tooling"
# -----------------------------------------------------------------------------
for t in pip pip2 pip2.7 virtualenv scram scramv1 condor_submit git curl tar; do
    p="$(command -v "$t" 2>/dev/null)"
    if [ -n "$p" ]; then printf '    %-14s %s\n' "$t" "$p"
    else printf '    %-14s %s\n' "$t" "(not found)"; fi
done

echo
echo "##############################################################################"
echo "## end of probe -- paste everything above"
echo "##############################################################################"
