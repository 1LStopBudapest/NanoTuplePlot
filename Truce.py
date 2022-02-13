import ROOT
from VarHandler import VarHandler
from Sample.SampleChain import SampleChain

#from Helper.VarCalc import *

sample = 'UL17V9_Full99mm'
year = 2016

tr = SampleChain(sample, 0, -1, year).getchain() #SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
getvar = VarHandler(tr=tr, isData=False, yr=year)

L = getvar.genClosest()
print(len(L))
print(len(L[0]))
print(len(L[1]))
print(len(L[2]))
