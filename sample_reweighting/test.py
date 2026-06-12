import math
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')  # prevents "no display" error on headless systems
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



decay_width_by_DeltaM_4bd_mstop500 = {10.:3.25e-17, 15.:3.52e-15, 20.:5.86e-14, 25.:4.48e-13, 30.:2.24e-12}

# Get sorted keys for interpolation
delta_m_keys = sorted(decay_width_by_DeltaM_4bd_mstop500.keys())
delta_m_vals = [decay_width_by_DeltaM_4bd_mstop500[k] for k in delta_m_keys]

Delta_m = 15
mStop = 500

print(delta_m_keys)
print(delta_m_vals)


delta_m_keys = np.array(delta_m_keys)
idx = (np.abs(delta_m_keys - Delta_m)).argmin()
print("closest key "+str(delta_m_keys[idx]))
print("closest value "+str(delta_m_vals[idx]))

width_500 = delta_m_vals[idx]
decay_width_by_mstop_4bd = width_500 * (500.0 / mStop)
