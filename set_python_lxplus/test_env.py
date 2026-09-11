#!/usr/bin/env python
"""
test_env.py -- verify the lxplus environment for this analysis.

    cmssw-el7
    source set_env.sh
    python test_env.py
    python test_env.py --rootfile /eos/.../merged_stopLL_500_490_BR_0.3_processed.root

Exits non-zero if anything is wrong, so it is usable as a check in a script.

Nothing is installed locally: every library is expected to come from CMSSW on
/cvmfs. This script checks that they are all importable and reports how each
version compares with the local (Higgs) machine, so a silent drift between the
two is visible rather than showing up later as slightly different plots.
"""

import os
import sys

# What the local (Higgs) machine has, for comparison. A difference is a warning,
# not an error -- these are patch-level gaps and the CMSSW set is self-consistent.
LOCAL_VERSIONS = {
    'numpy':      '1.16.2',
    'scipy':      '1.2.3',
    'matplotlib': '2.2.2',
    'pandas':     '0.24.2',
}
LOCAL_ROOT = '6.14/04'

# Needed by the active LL pipelines; a missing one is fatal.
REQUIRED = ('numpy', 'matplotlib', 'pandas')
# Used only by integral_test/, masspoint_2bd_test/ (curve_fit) -- warn if absent.
OPTIONAL = ('scipy',)

HERE = os.path.dirname(os.path.abspath(__file__))
# set_python_lxplus/ -> NanoTuplePlot/ -> test/
TESTDIR = os.path.dirname(os.path.dirname(HERE))

failures = []
warnings = []


def fail(msg):
    failures.append(msg)
    print("    FAIL  %s" % msg)


def warn(msg):
    warnings.append(msg)
    print("    WARN  %s" % msg)


def section(title):
    print("")
    print("-- %s %s" % (title, "-" * max(0, 72 - len(title))))


# ---------------------------------------------------------------------------
section("interpreter")
# ---------------------------------------------------------------------------
print("    python     : %s" % sys.version.replace("\n", " "))
print("    executable : %s" % sys.executable)
print("    maxunicode : %s" % sys.maxunicode)
print("    hostname   : %s" % os.uname()[1])
print("    USER       : %s" % os.environ.get('USER', '<unset>'))

if sys.version_info[:2] != (2, 7):
    fail("not Python 2.7 (this is %d.%d)" % sys.version_info[:2])

# set_env.sh should have put CMSSW's python on PATH. /usr/bin/python is the
# container's own 2.7.5 and cannot load CMSSW's ROOT.
if not sys.executable.startswith('/cvmfs/'):
    warn("python is %s, not CMSSW's on /cvmfs -- did you source set_env.sh?"
         % sys.executable)


# ---------------------------------------------------------------------------
section("libraries (all expected from CMSSW on /cvmfs)")
# ---------------------------------------------------------------------------
for name in REQUIRED + OPTIONAL:
    try:
        mod = __import__(name)
    except ImportError as e:
        if name in REQUIRED:
            fail("%-11s import failed: %s" % (name, e))
        else:
            warn("%-11s not available (only needed by integral_test/, "
                 "masspoint_2bd_test/)" % name)
        continue

    version = getattr(mod, '__version__', '?')
    path = getattr(mod, '__file__', '?')
    local = LOCAL_VERSIONS.get(name)

    print("    OK    %-11s %-9s %s" % (name, version, path))
    if local and version != local:
        warn("%s is %s here but %s on the local machine" % (name, version, local))


# ---------------------------------------------------------------------------
section("PyROOT")
# ---------------------------------------------------------------------------
ROOT = None
try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
    rver = ROOT.gROOT.GetVersion()
    print("    OK    ROOT        %-9s %s" % (rver, getattr(ROOT, '__file__', '?')))
    if rver != LOCAL_ROOT:
        warn("ROOT is %s here but %s on the local machine" % (rver, LOCAL_ROOT))
except Exception as e:
    fail("import ROOT failed: %r" % (e,))


# ---------------------------------------------------------------------------
section("ROOT + numpy together")
# ---------------------------------------------------------------------------
try:
    import numpy as np
except ImportError:
    np = None

if ROOT is not None and np is not None:
    try:
        h = ROOT.TH1F("probe", "probe", 50, -5, 5)
        for x in np.random.normal(0.0, 1.0, 2000):
            h.Fill(float(x))
        n = int(h.GetEntries())
        if n != 2000:
            fail("TH1F got %d entries, expected 2000" % n)
        else:
            print("    OK    filled TH1F with 2000 numpy values, mean=%.3f"
                  % h.GetMean())
    except Exception as e:
        fail("ROOT+numpy round trip failed: %r" % (e,))
else:
    print("    SKIP  (ROOT or numpy unavailable)")


# ---------------------------------------------------------------------------
section("matplotlib Agg rendering")
# ---------------------------------------------------------------------------
import shutil
import tempfile

outdir = None
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    outdir = tempfile.mkdtemp(prefix='test_env_')
    png = os.path.join(outdir, 'probe.png')

    fig = plt.figure(figsize=(2, 2))
    plt.plot([0, 1, 2], [0, 1, 4])
    fig.savefig(png)
    plt.close(fig)

    size = os.path.getsize(png)
    if size <= 0:
        fail("savefig produced an empty file")
    else:
        print("    OK    backend=%s, wrote %d bytes"
              % (matplotlib.get_backend(), size))
except Exception as e:
    fail("matplotlib Agg render failed: %r" % (e,))
finally:
    if outdir:
        shutil.rmtree(outdir, ignore_errors=True)


# ---------------------------------------------------------------------------
section("repo paths (Sample.Dir)")
# ---------------------------------------------------------------------------
# Dir.py picks its paths from os.uname()[1], so a change in lxplus hostnames
# would silently send output somewhere unexpected. Worth printing every run.
try:
    if TESTDIR not in sys.path:
        sys.path.insert(0, TESTDIR)
    from Sample import Dir
    print("    OK    Sample.Dir imported from %s" % Dir.__file__)
    for attr in ('userpath', 'plotDir', 'Xfiles'):
        print("          %-9s = %s" % (attr, getattr(Dir, attr, '<unset>')))
    for attr in ('plotDir', 'Xfiles'):
        p = getattr(Dir, attr, None)
        if p and not os.path.isdir(p):
            warn("Dir.%s does not exist yet: %s" % (attr, p))
except KeyError as e:
    # Dir.py does os.environ['USER'] unguarded; some batch contexts do not set it.
    fail("Sample.Dir raised KeyError %s -- likely $USER unset in this "
         "environment." % (e,))
except Exception as e:
    fail("importing Sample.Dir failed: %r" % (e,))


# ---------------------------------------------------------------------------
section("optional: open a real ntuple")
# ---------------------------------------------------------------------------
rootfile = None
if '--rootfile' in sys.argv:
    i = sys.argv.index('--rootfile')
    if i + 1 < len(sys.argv):
        rootfile = sys.argv[i + 1]

if rootfile and ROOT is not None:
    try:
        f = ROOT.TFile.Open(rootfile)
        if not f or f.IsZombie():
            fail("could not open %s" % rootfile)
        else:
            t = f.Get("Events")
            if not t:
                fail("no 'Events' tree in %s" % rootfile)
            else:
                t.GetEntry(0)
                print("    OK    %s: Events has %d entries"
                      % (rootfile, t.GetEntries()))
            f.Close()
    except Exception as e:
        fail("reading %s failed: %r" % (rootfile, e))
else:
    print("    SKIP  (pass --rootfile <path> to test real input)")
    print("          NOTE: Sample/FileList_LLStops_*_reworked.py hardcode local")
    print("          /mnt/newDisk/... paths that do not exist on lxplus. The")
    print("          event loops need those repointed before they run here.")


# ---------------------------------------------------------------------------
print("")
print("=" * 78)
if failures:
    print("FAILED -- %d problem(s):" % len(failures))
    for f in failures:
        print("    - %s" % f)
    if warnings:
        print("plus %d warning(s):" % len(warnings))
        for w in warnings:
            print("    - %s" % w)
    print("=" * 78)
    sys.exit(1)

if warnings:
    print("PASSED with %d warning(s):" % len(warnings))
    for w in warnings:
        print("    - %s" % w)
else:
    print("PASSED -- environment is ready")
print("=" * 78)
sys.exit(0)
