import os, sys
import ROOT
import types

import math
import numpy as np
import csv

print("basic imports done")

print("trying to see pyroot version")
# Print the PyROOT version
print(ROOT.gROOT.GetVersion())
print("done with pyroot")

print("trying to see python version")
print(sys.version)
print("done with python")

# --- lxplus -----------------------------------------------------------------
_host = os.uname()[1]
print("host name = "+str(_host))
if _host.startswith('lxplus') or 'cern.ch' in _host:
    print("host name starts with lxplus")
else:
    print("if block did not work")


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='MET_Data',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--br',           action='store',                    type=float,            default=0.8,                                               help="BR of the signal long lived sample. Ignore if bkg." )
    

    return argParser

options = get_parser().parse_args()

samples  = options.sample
year = options.year
branching_ratio = options.br

DataLumi=1.0

print("parser works")

print("attempting lib imports")

####################################################
#From here might fail
#################################################33
from FillHistos_LL_bothBR_newComb_cutFlow import FillHistosBothBR
sys.path.append('../../')
#sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.SampleChainSplittedBothBR import SampleChainSplittedBothBR
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

from Sample.FileList_LLStops_2018_reworked import samples as samples_LL

print("libraries imported")