#!/usr/bin/env python
"""
test_env.py -- verify the lxplus Python 2.7 + PyROOT environment.

    source setup_env.sh && python test_env.py
    python test_env.py --rootfile /eos/.../merged_stopLL_500_490_BR_0.3_processed.root

Exits non-zero if anything is wrong, so a condor job's exit code is meaningful.

The important check is the SHADOWED one: a virtualenv does not filter PYTHONPATH,
and CMSSW puts its own py2-numpy / py2-matplotlib on PYTHONPATH, so without the
prepend done by setup_env.sh the pinned versions are silently ignored. Printing
each module's __file__ is the only way to tell a correct env from that one.
"""

import os
import sys

# Versions pinned in requirements.txt, i.e. what the local (Higgs) machine has.
EXPECTED = {
    'numpy':      '1.16.2',
    'scipy':      '1.2.3',
    'matplotlib': '2.2.2',
    'pandas':     '0.24.2',
}

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = os.environ.get('STOP_ENV_VENV') or os.path.join(HERE, 'venv_folder')
# venv_lxplus/ -> NanoTuplePlot/ -> test/
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

# Any 2.7.x is fine -- 2.7.5, 2.7.12 and 2.7.15 are ABI-compatible. Only the
# major.minor and the UCS width actually matter.
if sys.version_info[:2] != (2, 7):
    fail("not Python 2.7 (this is %d.%d)" % sys.version_info[:2])
if sys.maxunicode <= 65535:
    fail("UCS2 build -- cp27mu manylinux wheels cannot be installed")


# ---------------------------------------------------------------------------
section("pinned libraries (must come from the venv, not CMSSW)")
# ---------------------------------------------------------------------------
for name in ('numpy', 'scipy', 'matplotlib', 'pandas'):
    try:
        mod = __import__(name)
    except ImportError as e:
        fail("%-11s import failed: %s" % (name, e))
        continue

    version = getattr(mod, '__version__', '?')
    path = getattr(mod, '__file__', '?')
    want = EXPECTED[name]

    if not os.path.abspath(path).startswith(os.path.abspath(VENV)):
        fail("%-11s %-9s SHADOWED-BY: %s" % (name, version, path))
        print("              (PYTHONPATH prepend did not take -- see setup_env.sh)")
    elif version != want:
        warn("%-11s %-9s OK from venv, but requirements.txt pins %s"
             % (name, version, want))
    else:
        print("    OK    %-11s %-9s %s" % (name, version, path))


# ---------------------------------------------------------------------------
section("PyROOT (must come from CMSSW on /cvmfs, NOT from the venv)")
# ---------------------------------------------------------------------------
ROOT = None
try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
    rver = ROOT.gROOT.GetVersion()
    rpath = getattr(ROOT, '__file__', '?')
    print("    OK    ROOT        %-9s %s" % (rver, rpath))
    if os.path.abspath(rpath).startswith(os.path.abspath(VENV)):
        fail("ROOT is being imported from the venv -- it should come from /cvmfs")
    if not rver.startswith('6.14'):
        warn("ROOT is %s; the local machine has 6.14/04. Usually fine, but any "
             "difference in histogram behaviour starts here." % rver)
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
        data = np.random.normal(0.0, 1.0, 2000)
        for x in data:
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
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    outdir = os.environ.get('MPLCONFIGDIR', '/tmp')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    png = os.path.join(outdir, 'test_env_probe.png')

    fig = plt.figure(figsize=(2, 2))
    plt.plot([0, 1, 2], [0, 1, 4])
    fig.savefig(png)
    plt.close(fig)

    size = os.path.getsize(png)
    if size <= 0:
        fail("savefig produced an empty file")
    else:
        print("    OK    backend=%s, wrote %d bytes to %s"
              % (matplotlib.get_backend(), size, png))
    os.remove(png)
except Exception as e:
    fail("matplotlib Agg render failed: %r" % (e,))


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
    # Dir.py does os.environ['USER'] unguarded; condor jobs may not set USER.
    fail("Sample.Dir raised KeyError %s -- likely $USER unset (condor). "
         "Set it in the job environment." % (e,))
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
    print("          event loops will need those repointed before they run here.")


# ---------------------------------------------------------------------------
print("")
print("=" * 78)
if failures:
    print("FAILED -- %d problem(s):" % len(failures))
    for f in failures:
        print("    - %s" % f)
    if warnings:
        print("plus %d warning(s)" % len(warnings))
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
