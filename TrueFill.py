import ROOT
import types
import os, sys

sys.path.append('../')
from Helper.VarCalc import *
from Helper.TreeVarSel_true import TreeVarSel_true
from Helper.MCWeight import MCWeight
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.IVFhelper import IVFhelper

class TrueFill():

    def __init__(self, histos, chain, year, nEvents, sample, DataLumi=1.0):
        self.histos = histos
        self.chain = chain
        self.year = year
        self.nEvents = nEvents
        self.sample = sample
        self.DataLumi = DataLumi
        self.isData = True if ('Run' in self.sample or 'Data' in self.sample) else False

        keylist = ['gStop_dx', 'gStop_dy', 'gStop_dz', 'gVtx_dx', 'gVtx_dy', 'gVtx_dz',
                   'gStop_gVtx_dx', 'gStop_gVtx_dy', 'gStop_gVtx_dz', 'gStop_gAStop_dx', 'gStop_gAStop_dy', 'gStop_gAStop_dz',
                   'gLSP_gStop_dx', 'gLSP_gStop_dy', 'gLSP_gStop_dz', 'PV_gVtx_dx', 'PV_gVtx_dy', 'PV_gVtx_dz',
                   'PV_gLSP_dx', 'PV_gLSP_dy', 'PV_gLSP_dz',
                   'gStop_gVtx_2D', 'gStop_gAStop_2D', 'gLSP_gStop_2D', 'PV_gVtx_2D', 'PV_gLSP_2D',
                   'gStop_gVtx_3D', 'gStop_gAStop_3D', 'gLSP_gStop_3D', 'PV_gVtx_3D', 'PV_gLSP_3D',
                   'gVtx_gLSP_dx', 'gVtx_gLSP_dy', 'gVtx_gLSP_dz', 'gVtx_gLSP_2D', 'gVtx_gLSP_3D',
                   'SV_gLSP_dx', 'SV_gLSP_dy', 'SV_gLSP_dz', 'SV_gLSP_2D', 'SV_gLSP_3D', 'nSV',
                   'SV_gVtx_dx', 'SV_gVtx_dy', 'SV_gVtx_dz', 'SV_gVtx_2D', 'SV_gVtx_3D',
                   'SV_gB_dx', 'SV_gB_dy', 'SV_gB_dz', 'SV_gB_2D','SV_gB_3D',
                   'gB_dx', 'gB_dy', 'gB_dz']

        self.vardic = {key: None for key in keylist}

    def fill(self):
        tr = self.chain
        vardic = self.vardic
        n_entries = tr.GetEntries()
        nevtcut = n_entries -1 if self.nEvents == - 1 else self.nEvents - 1
        print 'Running over total events: ', nevtcut+1

        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            tr.GetEntry(ientry) #ientry = i. event
            getsel = TreeVarSel_true(tr, self.year)
            getivf = IVFhelper(tr, self.isData, self.year)
            var = {key: None for key in vardic} #reseting the var dictionary for each event
            MCcorr = MCWeight(tr, self.year, self.sample).getTotalWeight()
            lumiscale = 1.0

            genStop = getsel.getGenPartStop()
            genVtx = getsel.getGenVtx()
            genAntiStop = getsel.getGenPartAntiStop()
            genLSP = getsel.getLSP()
            pv = getsel.getPV()
            sv = getivf.getSV()
            b = getsel.genB()

            #if getivf.IVFSelection() and getivf.HadronicSelection(): #after IVF cut
            if 1 > 0: #before IVF cut
                var['nSV'] = getivf.getNSV()
                var['gStop_dx'] = genStop['x']*10 #mm
                var['gStop_dy'] = genStop['y']*10
                var['gStop_dz'] = genStop['z']    #cm
                var['gVtx_dx'] = genVtx['x']*10
                var['gVtx_dy'] = genVtx['y']*10
                var['gVtx_dz'] = genVtx['z']
                var['gStop_gVtx_dx'] = getsel.distance(genVtx, genStop, 'x')*10000 #um
                var['gStop_gVtx_dy'] = getsel.distance(genVtx, genStop, 'y')*10000
                var['gStop_gVtx_dz'] = getsel.distance(genVtx, genStop, 'z')*10000
                var['gStop_gAStop_dx'] = getsel.distance(genAntiStop, genStop, 'x')*10000
                var['gStop_gAStop_dy'] = getsel.distance(genAntiStop, genStop, 'y')*10000
                var['gStop_gAStop_dz'] = getsel.distance(genAntiStop, genStop, 'z')*10000
                var['PV_gVtx_dx'] = getsel.distance(genVtx, pv, 'x')*10 #mm
                var['PV_gVtx_dy'] = getsel.distance(genVtx, pv, 'y')*10
                var['PV_gVtx_dz'] = getsel.distance(genVtx, pv, 'z')*10
                var['gStop_gVtx_2D'] = sqrt(var['gStop_gVtx_dx']**2 + var['gStop_gVtx_dy']**2)
                var['gStop_gAStop_2D'] = sqrt(var['gStop_gAStop_dx']**2 + var['gStop_gAStop_dy']**2)
                var['PV_gVtx_2D'] = sqrt(var['PV_gVtx_dx']**2 + var['PV_gVtx_dy']**2)
                var['gStop_gVtx_3D'] = sqrt(var['gStop_gVtx_dx']**2 + var['gStop_gVtx_dy']**2 + var['gStop_gVtx_dz']**2)
                var['gStop_gAStop_3D'] = sqrt(var['gStop_gAStop_dx']**2 + var['gStop_gAStop_dy']**2 + var['gStop_gAStop_dz']**2)
                var['PV_gVtx_3D'] = sqrt(var['PV_gVtx_dx']**2 + var['PV_gVtx_dy']**2 + var['PV_gVtx_dz']**2)
                if len(genLSP) > 0:
                    var['gLSP_gStop_dx'] = [d for d in getsel.listDist(genLSP, [genStop], 'x')]
                    var['gLSP_gStop_dy'] = [d for d in getsel.listDist(genLSP, [genStop], 'y')]
                    var['gLSP_gStop_dz'] = [d for d in getsel.listDist(genLSP, [genStop], 'z')]
                    var['PV_gLSP_dx'] = [d for d in getsel.listDist(genLSP, [pv], 'x')] #d*10000 <--> Prompt
                    var['PV_gLSP_dy'] = [d for d in getsel.listDist(genLSP, [pv], 'y')]
                    var['PV_gLSP_dz'] = [d for d in getsel.listDist(genLSP, [pv], 'z')]
                    var['gLSP_gStop_2D'] = [sqrt(var['gLSP_gStop_dx'][i]**2 + var['gLSP_gStop_dy'][i]**2) for i in range(len(var['gLSP_gStop_dx']))]
                    var['PV_gLSP_2D'] = [sqrt(var['PV_gLSP_dx'][i]**2 + var['PV_gLSP_dy'][i]**2) for i in range(len(var['PV_gLSP_dx']))]
                    var['gLSP_gStop_3D'] = [sqrt(var['gLSP_gStop_dx'][i]**2 + var['gLSP_gStop_dy'][i]**2 + var['gLSP_gStop_dz'][i]**2) for i in range(len(var['gLSP_gStop_dx']))]
                    var['PV_gLSP_3D'] = [sqrt(var['PV_gLSP_dx'][i]**2 + var['PV_gLSP_dy'][i]**2 + var['PV_gLSP_dz'][i]**2) for i in range(len(var['PV_gLSP_dx']))]
                    var['gVtx_gLSP_dx'] = [d for d in getsel.listDist([genVtx], genLSP, 'x')] #d*10000 <--> Prompt
                    var['gVtx_gLSP_dy'] = [d for d in getsel.listDist([genVtx], genLSP, 'y')]
                    var['gVtx_gLSP_dz'] = [d for d in getsel.listDist([genVtx], genLSP, 'z')]
                    var['gVtx_gLSP_2D'] = [sqrt(var['gVtx_gLSP_dx'][i]**2 + var['gVtx_gLSP_dy'][i]**2) for i in range(len(var['gVtx_gLSP_dx']))]
                    var['gVtx_gLSP_3D'] = [sqrt(var['gVtx_gLSP_dx'][i]**2 + var['gVtx_gLSP_dy'][i]**2 + var['gVtx_gLSP_dz'][i]**2) for i in range(len(var['gVtx_gLSP_dx']))]
                    if len(sv) > 0:
                        var['SV_gLSP_dx'] = [d for d in getsel.listDist(sv, genLSP, 'x')]
                        var['SV_gLSP_dy'] = [d for d in getsel.listDist(sv, genLSP, 'y')]
                        var['SV_gLSP_dz'] = [d for d in getsel.listDist(sv, genLSP, 'z')]
                        var['SV_gLSP_2D'] = [sqrt(var['SV_gLSP_dx'][i]**2 + var['SV_gLSP_dy'][i]**2) for i in range(len(var['SV_gLSP_dx']))]
                        var['SV_gLSP_3D'] = [sqrt(var['SV_gLSP_dx'][i]**2 + var['SV_gLSP_dy'][i]**2 + var['SV_gLSP_dz'][i]**2) for i in range(len(var['SV_gLSP_dx']))]
                        var['SV_gVtx_dx'] = [d for d in getsel.listDist(sv, [genVtx], 'x')]
                        var['SV_gVtx_dy'] = [d for d in getsel.listDist(sv, [genVtx], 'y')]
                        var['SV_gVtx_dz'] = [d for d in getsel.listDist(sv, [genVtx], 'z')]
                        var['SV_gVtx_2D'] = [sqrt(var['SV_gVtx_dx'][i]**2 + var['SV_gVtx_dy'][i]**2) for i in range(len(var['SV_gVtx_dx']))]
                        var['SV_gVtx_3D'] = [sqrt(var['SV_gVtx_dx'][i]**2 + var['SV_gVtx_dy'][i]**2 + var['SV_gVtx_dz'][i]**2) for i in range(len(var['SV_gVtx_dx']))]
                        var['SV_gB_dx'] = [d for d in getsel.listDist(sv, b, 'x')]
                        var['SV_gB_dy'] = [d for d in getsel.listDist(sv, b, 'y')]
                        var['SV_gB_dz'] = [d for d in getsel.listDist(sv, b, 'z')]
                        var['SV_gB_2D'] = [sqrt(var['SV_gB_dx'][i]**2 + var['SV_gB_dy'][i]**2) for i in range(len(var['SV_gB_dx']))]
                        var['SV_gB_3D'] = [sqrt(var['SV_gB_dx'][i]**2 + var['SV_gB_dy'][i]**2 + var['SV_gB_dz'][i]**2) for i in range(len(var['SV_gB_dx']))]
                        var['gB_dx'] = [d['x'] for d in b]
                        var['gB_dy'] = [d['y'] for d in b]
                        var['gB_dz'] = [d['z'] for d in b]

            for key in self.histos:
                if key in var.keys():
                    if var[key] is not None:
                        if isinstance(var[key], types.ListType):
                            for x in var[key]: Fill1D(self.histos[key], x, lumiscale * MCcorr)
                        else:
                            Fill1D(self.histos[key], var[key], lumiscale * MCcorr)
                else:
                    print "You are trying to fill the histos for the keys ", key, " which are missing in var dictionary"
