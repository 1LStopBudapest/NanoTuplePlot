#!/usr/bin/env python
"""
probe_worker.py -- run ONE condor job to find out what a CERN batch node looks
like, before launching 1750 real ones.

The decisive question: Sample/Dir.py and Sample/FileList_LLStops_*_reworked.py
choose between the lxplus (/eos/...) and local (/mnt/newDisk/...) paths with

    _host = os.uname()[1]
    if _host.startswith('lxplus') or 'cern.ch' in _host:

A worker node is called something like b9g03p3124, which may match neither.
This prints what the test actually sees there, plus which branch it took and
whether the resulting sample path exists.

Read the "VERDICT" block at the end of the .out file.
"""

import os
import sys
import socket

def show(label, value):
    print("    %-22s %s" % (label, value))

def hr(title):
    print("")
    print("=" * 74)
    print("== " + title)
    print("=" * 74)

hr("1. Identity -- what the site test sees")
uname_host = os.uname()[1]
show("os.uname()[1]", repr(uname_host))
show("socket.gethostname()", repr(socket.gethostname()))
try:
    show("socket.getfqdn()", repr(socket.getfqdn()))
except Exception as e:
    show("socket.getfqdn()", "FAILED %r" % (e,))
show("$HOSTNAME", repr(os.environ.get('HOSTNAME', '<unset>')))
show("$USER", repr(os.environ.get('USER', '<unset>')))
show("cwd", os.getcwd())

# This is the exact expression the four files use.
matches = uname_host.startswith('lxplus') or 'cern.ch' in uname_host
show("SITE TEST MATCHES?", "YES -> lxplus paths" if matches else "NO  -> LOCAL paths (wrong here)")

hr("2. Container / interpreter")
try:
    show("redhat-release", open('/etc/redhat-release').read().strip())
except Exception as e:
    show("redhat-release", "unreadable: %r" % (e,))
show("python", sys.executable)
show("version", sys.version.replace("\n", " "))

hr("3. ROOT")
try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
    show("ROOT version", ROOT.gROOT.GetVersion())
    show("ROOT.__file__", ROOT.__file__)
except Exception as e:
    show("import ROOT", "FAILED %r" % (e,))

hr("4. numpy / matplotlib / pandas")
for m in ('numpy', 'matplotlib', 'pandas'):
    try:
        mod = __import__(m)
        show(m, "%s  %s" % (getattr(mod, '__version__', '?'), getattr(mod, '__file__', '?')))
    except Exception as e:
        show(m, "FAILED %r" % (e,))

hr("5. Which branch Sample/Dir.py and the FileList actually took")
sys.path.append('../../')
first_path = None
try:
    from Sample import Dir
    for a in ('userpath', 'plotDir', 'Xfiles'):
        show("Dir." + a, getattr(Dir, a, '<unset>'))
    p = getattr(Dir, 'plotDir', None)
    if p:
        show("plotDir exists?", os.path.isdir(p))
except Exception as e:
    show("import Sample.Dir", "FAILED %r" % (e,))

try:
    from Sample.FileList_LLStops_2018_reworked import samples as s18
    show("n sample keys", len(s18))
    key = 'Sig_Splitted_500_490_0.3'
    if key in s18:
        first_path = s18[key][0]
        show(key, first_path)
        show("  starts with /eos?", first_path.startswith('/eos'))
        show("  file exists?", os.path.exists(first_path))
    else:
        show(key, "KEY MISSING")
except Exception as e:
    show("import FileList", "FAILED %r" % (e,))

hr("6. Can we actually open a sample file?")
if first_path and os.path.exists(first_path):
    try:
        import ROOT
        f = ROOT.TFile.Open(first_path)
        if not f or f.IsZombie():
            show("TFile.Open", "FAILED (zombie)")
        else:
            t = f.Get("Events")
            show("Events entries", t.GetEntries() if t else "NO Events TREE")
            f.Close()
    except Exception as e:
        show("TFile.Open", "FAILED %r" % (e,))
else:
    show("skipped", "no readable sample path -- see section 5")

hr("7. Can we write where the job needs to?")
for label, d in (("cwd (repo dir)", os.getcwd()),
                 ("Dir.plotDir", getattr(sys.modules.get('Sample.Dir'), 'plotDir', None))):
    if not d:
        continue
    probe = os.path.join(d, '.probe_write_test')
    try:
        fh = open(probe, 'w')
        fh.write('x')
        fh.close()
        os.remove(probe)
        show(label, "WRITABLE (%s)" % d)
    except Exception as e:
        show(label, "NOT writable (%s): %r" % (d, e))

hr("VERDICT")
if matches:
    print("    Hostname test MATCHES on this worker -- no code change needed.")
else:
    print("    Hostname test DOES NOT MATCH on this worker.")
    print("    os.uname()[1] = %r" % uname_host)
    print("    -> Dir.py and the FileLists fell back to the LOCAL /mnt/newDisk")
    print("       branch, so the 1750 real jobs would all fail to find input.")
    print("    -> Fix the site test in Sample/Dir.py and the three")
    print("       Sample/FileList_LLStops_*_reworked.py before submitting.")
print("")
