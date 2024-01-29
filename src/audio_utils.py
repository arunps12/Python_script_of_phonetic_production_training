# audio_utils.py
import soundfile as sf
import sounddevice as sd
import numpy as np
from psychopy import event

class AudioRecorder:
    def __init__(self):
        self.buffer = []
        #self.window = window

    def callback(self, indata, frames, time, status):
        if status:
            print(f"Error in callback: {status}")
        # Append the incoming audio data to the buffer
        self.buffer.append(indata.copy())

    def record_audio(self, duration, fs, window, w):
        with sd.InputStream(callback=self.callback, samplerate = fs, channels=1):
            w.draw()
            window.flip()
            event.waitKeys(1.5)
            w.autoDraw = False
            sd.sleep(int(duration))
        # Concatenate the chunks in the buffer to get the full recording
        y = np.concatenate(self.buffer, axis=0)
        return y

    def clear_buffer(self):
        self.buffer.clear()

    def play_audio(self, audio_path):
        audio_data, sample_rate = sf.read(audio_path)
        sd.play(audio_data, sample_rate)
        sd.wait()  # Wait for the audio to finish playing
