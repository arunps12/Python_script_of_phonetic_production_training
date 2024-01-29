import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

def rms(Y):
    RMS = np.sqrt(np.mean(np.abs(Y) ** 2))
    return RMS

def frmnts(a,Fs):
    const = Fs / (2*np.pi)
    rts = np.roots(a)
    save = []
    bandw = []
    for rt in rts:
        re, im = np.real(rt), np.imag(rt)
        formn = const * np.arctan2(im, re)
        bw = -0.5 * const * np.log(np.abs(rt))
        if 90 < formn < 4000 and bw < 500:
            save.append(formn)
            bandw.append(bw)
    # Sort formants by frequency
    y = sorted(save)
    return y[0], y[1], y[2]


def onset_offset(infile, make_plot=False):
    # Read the sound
    y, fs = librosa.load(infile, mono=True)

    # High pass filter the sound
    y = librosa.effects.preemphasis(y)
    
    # Automatic noise level estimation (th_noise)
    dt = int(round(0.05 * fs))
    Ndt = int(len(y) / dt)
    noise_est = np.min(np.sqrt(np.mean(np.reshape(y[:dt * Ndt], (dt, Ndt))**2, axis=0)))
    th_noise = 6 * noise_est

    # Compute a characteristic signal (Yp)
    dt = int(round(0.01 * fs))  # minimum half wave distance
    yp = (y > th_noise).astype(int)
    yp = np.convolve(np.abs(yp), np.ones(dt), mode='same')
    yp[[0, -1]] = 0

    # Find onset and offset
    thp = dt / 50
    center = np.argmax(yp)
    onset = np.where(np.diff(yp[:center] > thp))[0][-1]
    offset = np.where(np.diff(yp[center:] > thp))[0][0] + center

    # Assign extreme timings if not identified
    if onset.size == 0:
        onset = 0
    if offset.size == 0:
        offset = len(y)

    # Refine the onset and offset
    th_onset = np.percentile(np.abs(y[onset:offset]), 99) / 5
    onset_high = np.where(np.abs(y[onset:offset]) > th_onset)[0][0] + onset
    offset_high = np.where(np.abs(y[onset:offset]) > th_onset)[0][-1] + onset

    # Find the optimal center (for 100 ms analysis window)
    dt = int(round(0.1 * fs))  # minimum half wave distance
    yp = np.convolve(np.abs(y), np.ones(dt), mode='same')
    center = np.argmax(yp)

    # Change to seconds
    onset /= fs
    offset /= fs
    onset_high /= fs
    offset_high /= fs
    center /= fs

    # Make plots if asked for
    if make_plot:
        plt.figure()
        plt.plot(np.arange(len(y)) / fs, y, 'k')
        plt.axvline(x=onset, color='g', linestyle='-', linewidth=2, label='Onset')
        plt.axvline(x=offset, color='g', linestyle='-', linewidth=2, label='Offset')
        plt.axvline(x=onset_high, color='r', linestyle='-', linewidth=2, label='Onset High')
        plt.axvline(x=offset_high, color='r', linestyle='-', linewidth=2, label='Offset High')
        plt.axvline(x=center, color='c', linestyle='-', linewidth=3, label='Center')
        plt.legend()
        plt.show()

    return onset, offset, onset_high, offset_high, center