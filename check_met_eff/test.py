import numpy as np
from stops_13TeV import xsecNNLL 

def get_xsec(mst = 200.):
  # xsec returned in fb
  #stoparray = [200., 250., 300., 350., 400., 450., 500., 550., 600., 650., 700., 750., 800., 850., 900., 950., 1000.]
  #xsecarray = [0.755E+05, 0.248E+05, 0.100E+05, 0.443E+04, 0.215E+04, 0.111E+04, 0.609E+03, 0.347E+03, 0.205E+03, 0.125E+03, 0.783E+02, 0.5E+02, 0.326E+02, 0.216E+02, 0.145E+02, 0.991E+01, 0.683E+01]#https://github.com/HephyAnalysisSW/StopsCompressed/blob/master/Tools/python/xSecSusyData/stops_13TeV.py

  masses = np.array(sorted(xsecNNLL.keys()))

  # Extract cross sections (first value of each tuple)
  xsecs_pb = np.array([xsecNNLL[m][0] for m in masses])
  # Convert to femtobarns (1 pb = 1000 fb)
  xsecs_fb = xsecs_pb * 1000.0

  print(masses)
  print(xsecs_pb)

  if mst < masses[0]: return -1.
  if mst > masses[-1]: return -1.
  xsec = np.interp(mst, masses, xsecs_fb)   
  return xsec

print(get_xsec(300))
