import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.PlotHelper import *

def get_parser():
    ''' Argument parser.                                                                                                                                                 
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument(
    '-l', '--samplelist',  # either of this switches
    nargs='+',       # one or more parameters to this switch
    type=str,        # /parameters/ are ints
    dest='alist',     # store in 'list'.
    default=['WJetsToLNu', 'MET_Data'],      #last sample should be data as to be consistent with StackHists funtion.
    )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist


files = []
doplots = True

for sl in samplelists:
    if os.path.exists('StackHist_'+sl+'.root'):
        files.append(ROOT.TFile.Open('StackHist_'+sl+'.root'))
    elif os.path.exists(plotDir+'StackFiles/StackHist_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'StackFiles/StackHist_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for',sl,'sample does not exist. Please run python StackHistMaker.py --sample',sl

if doplots :
    StackHists(files, samplelists, 'MET', plotDir, 'cut')
    StackHists(files, samplelists, 'Leppt', plotDir, 'cut')
    StackHists(files, samplelists, 'LepMT', plotDir, 'cut')
    StackHists(files, samplelists, 'HT', plotDir, 'cut')
    StackHists(files, samplelists, 'CT1', plotDir, 'cut')
    StackHists(files, samplelists, 'CT2', plotDir, 'cut')
    StackHists(files, samplelists, 'ISRJetPt', plotDir, 'cut')
    StackHists(files, samplelists, 'ISRJetEta', plotDir, 'cut')
    StackHists(files, samplelists, '2ndJetPt', plotDir, 'cut')
    StackHists(files, samplelists, '2ndJetEta', plotDir, 'cut')
    StackHists(files, samplelists, '3rdJetPt', plotDir, 'cut')
    StackHists(files, samplelists, '3rdJetEta', plotDir, 'cut')
    StackHists(files, samplelists, 'JetPt', plotDir, 'cut')
    StackHists(files, samplelists, 'JetEta', plotDir, 'cut')
    StackHists(files, samplelists, 'BjetPt', plotDir, 'cut')
    StackHists(files, samplelists, 'Njet20', plotDir, 'cut')
    StackHists(files, samplelists, 'Njet30', plotDir, 'cut')
    StackHists(files, samplelists, 'Nbjet20', plotDir, 'cut')
    StackHists(files, samplelists, 'Nbjet30', plotDir, 'cut')
    StackHists(files, samplelists, 'DeltaPhi_Jets', plotDir, 'cut')
    StackHists(files, samplelists, 'DeltaPhi_Jets60', plotDir, 'cut')
    StackHists(files, samplelists, '1stBjetPt', plotDir, 'cut')
    StackHists(files, samplelists, '1stBjetEta', plotDir, 'cut')
