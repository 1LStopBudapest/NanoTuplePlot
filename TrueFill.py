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
                   'gB_dx', 'gB_dy', 'gB_dz',
                   'gB_gLSP_dx', 'gB_gLSP_dy', 'gB_gLSP_dz', 'gB_gLSP_2D', 'gB_gLSP_3D',
                   'SV_dx', 'SV_dy', 'SV_dz',
                   'PV_dx', 'PV_dy', 'PV_dz',
                   'SV_PV_dx', 'SV_PV_dy', 'SV_PV_dz', 'SV_PV_2D', 'SV_PV_3D',
                   'dec_dx', 'dec_dy', 'dec_dz', 'dec_2D', 'dec_3D',
                   'PV_gStop_dx', 'PV_gStop_dy', 'PV_gStop_dz', 'PV_gStop_2D', 'PV_gStop_3D',
                   'SV_gStop_dx', 'SV_gStop_dy', 'SV_gStop_dz', 'SV_gStop_2D', 'SV_gStop_3D']

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
            genLSP_S = getsel.getLSP_S()
            genLSP_A = getsel.getLSP_A()
            pv = getsel.getPV()
            sv = getivf.getSV()
            b_S = getsel.getB_S()
            b_A = getsel.getB_A()
            stop106 = getsel.get106()

            #if getivf.IVFSelection() and getivf.HadronicSelection(): #after IVF cut
            if 1 > 0: #before IVF cut
                var['nSV'] = getivf.getNSV()
                var['gStop_dx'] = genStop['x']*10 #mm
                var['gStop_dy'] = genStop['y']*10
                var['gStop_dz'] = genStop['z']    #cm
                var['gVtx_dx'] = genVtx['x']*10
                var['gVtx_dy'] = genVtx['y']*10
                var['gVtx_dz'] = genVtx['z']
                var['PV_dx'] = pv['x']
                var['PV_dy'] = pv['y']
                var['PV_dz'] = pv['z']
                var['gStop_gVtx_dx'] = getsel.distance(genVtx, genStop, 'x')*10000 #um
                var['gStop_gVtx_dy'] = getsel.distance(genVtx, genStop, 'y')*10000
                var['gStop_gVtx_dz'] = getsel.distance(genVtx, genStop, 'z')*10000
                var['gStop_gVtx_2D'] = sqrt(var['gStop_gVtx_dx']**2 + var['gStop_gVtx_dy']**2)
                var['gStop_gVtx_3D'] = sqrt(var['gStop_gVtx_dx']**2 + var['gStop_gVtx_dy']**2 + var['gStop_gVtx_dz']**2)
                var['gStop_gAStop_dx'] = getsel.distance(genAntiStop, genStop, 'x')*10000
                var['gStop_gAStop_dy'] = getsel.distance(genAntiStop, genStop, 'y')*10000
                var['gStop_gAStop_dz'] = getsel.distance(genAntiStop, genStop, 'z')*10000
                var['gStop_gAStop_2D'] = sqrt(var['gStop_gAStop_dx']**2 + var['gStop_gAStop_dy']**2)
                var['gStop_gAStop_3D'] = sqrt(var['gStop_gAStop_dx']**2 + var['gStop_gAStop_dy']**2 + var['gStop_gAStop_dz']**2)
                var['PV_gVtx_dx'] = getsel.distance(genVtx, pv, 'x')*10
                var['PV_gVtx_dy'] = getsel.distance(genVtx, pv, 'y')*10
                var['PV_gVtx_dz'] = getsel.distance(genVtx, pv, 'z')*10
                var['PV_gVtx_2D'] = sqrt(var['PV_gVtx_dx']**2 + var['PV_gVtx_dy']**2)
                var['PV_gVtx_3D'] = sqrt(var['PV_gVtx_dx']**2 + var['PV_gVtx_dy']**2 + var['PV_gVtx_dz']**2)
                var['PV_gStop_dx'] = getsel.distance(pv, genStop, 'x')*10
                var['PV_gStop_dy'] = getsel.distance(pv, genStop, 'y')*10
                var['PV_gStop_dz'] = getsel.distance(pv, genStop, 'z')*10
                var['PV_gStop_2D'] = sqrt(var['PV_gStop_dx']**2 + var['PV_gStop_dy']**2)
                var['PV_gStop_3D'] = sqrt(var['PV_gStop_dx']**2 + var['PV_gStop_dy']**2 + var['PV_gStop_dz']**2)
                if len(stop106) > 0:
                    var['dec_dx'] = getsel.distance(stop106, genStop, 'x') #decay length
                    var['dec_dy'] = getsel.distance(stop106, genStop, 'y')
                    var['dec_dz'] = getsel.distance(stop106, genStop, 'z')
                    var['dec_2D'] = sqrt(var['dec_dx']**2 + var['dec_dy']**2)
                    var['dec_3D'] = sqrt(var['dec_dx']**2 + var['dec_dy']**2 + var['dec_dz']**2)
                if len(genLSP_S) > 0 and len(genLSP_A) > 0:
                    var['gLSP_gStop_dx'] = [getsel.distance(genLSP_S, genStop, 'x'), getsel.distance(genLSP_A, genAntiStop, 'x')]
                    var['gLSP_gStop_dy'] = [getsel.distance(genLSP_S, genStop, 'y'), getsel.distance(genLSP_A, genAntiStop, 'y')]
                    var['gLSP_gStop_dz'] = [getsel.distance(genLSP_S, genStop, 'z'), getsel.distance(genLSP_A, genAntiStop, 'z')]
                    var['gLSP_gStop_2D'] = [sqrt(var['gLSP_gStop_dx'][i]**2 + var['gLSP_gStop_dy'][i]**2) for i in range(len(var['gLSP_gStop_dx']))]
                    var['gLSP_gStop_3D'] = [sqrt(var['gLSP_gStop_dx'][i]**2 + var['gLSP_gStop_dy'][i]**2 + var['gLSP_gStop_dz'][i]**2) for i in range(len(var['gLSP_gStop_dx']))]
                    var['PV_gLSP_dx'] = [getsel.distance(genLSP_S, pv, 'x'), getsel.distance(genLSP_A, pv, 'x')]  #d*10 <--> Prompt
                    var['PV_gLSP_dy'] = [getsel.distance(genLSP_S, pv, 'y'), getsel.distance(genLSP_A, pv, 'y')]
                    var['PV_gLSP_dz'] = [getsel.distance(genLSP_S, pv, 'z'), getsel.distance(genLSP_A, pv, 'z')]
                    var['PV_gLSP_2D'] = [sqrt(var['PV_gLSP_dx'][i]**2 + var['PV_gLSP_dy'][i]**2) for i in range(len(var['PV_gLSP_dx']))]
                    var['PV_gLSP_3D'] = [sqrt(var['PV_gLSP_dx'][i]**2 + var['PV_gLSP_dy'][i]**2 + var['PV_gLSP_dz'][i]**2) for i in range(len(var['PV_gLSP_dx']))]
                    var['gVtx_gLSP_dx'] = [getsel.distance(genLSP_S, genVtx, 'x'), getsel.distance(genLSP_A, genVtx, 'x')] #d*10000 <--> Prompt
                    var['gVtx_gLSP_dy'] = [getsel.distance(genLSP_S, genVtx, 'y'), getsel.distance(genLSP_A, genVtx, 'y')]
                    var['gVtx_gLSP_dz'] = [getsel.distance(genLSP_S, genVtx, 'z'), getsel.distance(genLSP_A, genVtx, 'z')]
                    var['gVtx_gLSP_2D'] = [sqrt(var['gVtx_gLSP_dx'][i]**2 + var['gVtx_gLSP_dy'][i]**2) for i in range(len(var['gVtx_gLSP_dx']))]
                    var['gVtx_gLSP_3D'] = [sqrt(var['gVtx_gLSP_dx'][i]**2 + var['gVtx_gLSP_dy'][i]**2 + var['gVtx_gLSP_dz'][i]**2) for i in range(len(var['gVtx_gLSP_dx']))]
                    if len(sv) > 0:
                        var['SV_gLSP_dx'] = [getsel.smallestDist(genLSP_S, sv, 'x'), getsel.smallestDist(genLSP_A, sv, 'x')]
                        var['SV_gLSP_dy'] = [getsel.smallestDist(genLSP_S, sv, 'y'), getsel.smallestDist(genLSP_A, sv, 'y')]
                        var['SV_gLSP_dz'] = [getsel.smallestDist(genLSP_S, sv, 'z'), getsel.smallestDist(genLSP_A, sv, 'z')]
                        var['SV_gLSP_2D'] = [getsel.smallestDist2D(genLSP_S, sv), getsel.smallestDist2D(genLSP_A, sv)]
                        var['SV_gLSP_3D'] = [getsel.smallestDist3D(genLSP_S, sv), getsel.smallestDist3D(genLSP_A, sv)]
                        var['SV_gVtx_dx'] = getsel.smallestDist(genVtx, sv, 'x')
                        var['SV_gVtx_dy'] = getsel.smallestDist(genVtx, sv, 'y')
                        var['SV_gVtx_dz'] = getsel.smallestDist(genVtx, sv, 'z')
                        var['SV_gVtx_2D'] = getsel.smallestDist2D(genVtx, sv)
                        var['SV_gVtx_3D'] = getsel.smallestDist3D(genVtx, sv)
                        var['SV_dx'] = [s['x'] for s in sv]
                        var['SV_dy'] = [s['y'] for s in sv]
                        var['SV_dz'] = [s['z'] for s in sv]
                        var['SV_PV_dx'] = getsel.smallestDist(pv, sv, 'x')
                        var['SV_PV_dy'] = getsel.smallestDist(pv, sv, 'y')
                        var['SV_PV_dz'] = getsel.smallestDist(pv, sv, 'z')
                        var['SV_PV_2D'] = getsel.smallestDist2D(pv, sv)
                        var['SV_PV_3D'] = getsel.smallestDist3D(pv, sv)
                        var['SV_gStop_dx'] = getsel.smallestDist(genStop, sv, 'x')
                        var['SV_gStop_dy'] = getsel.smallestDist(genStop, sv, 'y')
                        var['SV_gStop_dz'] = getsel.smallestDist(genStop, sv, 'z')
                        var['SV_gStop_2D'] = getsel.smallestDist2D(genStop, sv)
                        var['SV_gStop_3D'] = getsel.smallestDist3D(genStop, sv)
                        if len(b_S) > 0 and len(b_A) > 0:
                            var['SV_gB_dx'] = [getsel.smallestDist(b_S, sv, 'x'), getsel.smallestDist(b_A, sv, 'x')]
                            var['SV_gB_dy'] = [getsel.smallestDist(b_S, sv, 'y'), getsel.smallestDist(b_A, sv, 'y')]
                            var['SV_gB_dz'] = [getsel.smallestDist(b_S, sv, 'z'), getsel.smallestDist(b_A, sv, 'z')]
                            var['SV_gB_2D'] = [getsel.smallestDist2D(b_S, sv), getsel.smallestDist2D(b_A, sv)]
                            var['SV_gB_3D'] = [getsel.smallestDist3D(b_S, sv), getsel.smallestDist3D(b_A, sv)]
                            var['gB_dx'] = [d['x'] for d in [b_S,b_A]] #d*10 <--> Prompt
                            var['gB_dy'] = [d['y'] for d in [b_S,b_A]]
                            var['gB_dz'] = [d['z'] for d in [b_S,b_A]]
                            var['gB_gLSP_dx'] = [getsel.distance(b_S, genLSP_S, 'x'), getsel.distance(b_A, genLSP_A, 'x')]
                            var['gB_gLSP_dy'] = [getsel.distance(b_S, genLSP_S, 'y'), getsel.distance(b_A, genLSP_A, 'y')]
                            var['gB_gLSP_dz'] = [getsel.distance(b_S, genLSP_S, 'z'), getsel.distance(b_A, genLSP_A, 'z')]
                            var['gB_gLSP_2D'] = [sqrt(var['gB_gLSP_dx'][i]**2 + var['gB_gLSP_dy'][i]**2) for i in range(2)]
                            var['gB_gLSP_3D'] = [sqrt(var['gB_gLSP_dx'][i]**2 + var['gB_gLSP_dy'][i]**2 + var['gB_gLSP_dz'][i]**2) for i in range(2)]

            for key in self.histos:
                if key in var.keys():
                    if var[key] is not None:
                        if isinstance(var[key], types.ListType):
                            for x in var[key]: Fill1D(self.histos[key], x, lumiscale * MCcorr)
                        else:
                            Fill1D(self.histos[key], var[key], lumiscale * MCcorr)
                else:
                    print "You are trying to fill the histos for the keys ", key, " which are missing in var dictionary"
