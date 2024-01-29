import numpy as np

def rms(Y):
    RMS = np.sqrt(np.mean(np.abs(Y) ** 2))
    return RMS