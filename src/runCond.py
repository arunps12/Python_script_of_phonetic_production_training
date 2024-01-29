import os
import sys
import numpy as np
import sounddevice as sd
import soundfile as sf
from psychopy import visual, core, event, sound, monitors
import random
from PIL import Image
import imageio
from scipy.signal import hamming, lfilter, resample
import librosa
import pdb
import pickle
import traceback
import datetime
import re
from utils import rms, frmnts, onset_offset
from audio_utils import AudioRecorder

def runCond(nsubj, BlockNum, group, vowel, numRepetitions, numTokens, BWD, BWOD, fid,NPersistFB, TrimPortion, HamWind, RecordDuration, ScreenSize, whichScreen, window, FeedbackAxes, FeedbackScale, RMS, RMSIncrement, condition_number, block_number, FBRadius, DEBUG):
    persistent_feedback = np.empty((0, 2))
    PFBVALID = 1
    WarnTextCol = [175, 175, 175]
    PFB_Col = np.column_stack([np.linspace(225, 175, NPersistFB)] * 3)
    #fs = 11000
    #duration = RecordDuration
    #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=(255, 255, 255))

    #if os.name == 'posix' or ('Darwin' in os.uname()):
        #audio_info = sd.query_devices(sd.default.device, 'input')
        #recorder = sd.InputStream(device=audio_info['device'], channels=1, samplerate=fs, dtype=np.int16)
    #else:
        #recorder = sd.rec(int(fs * duration), channels=1, dtype=np.int16)
        #sd.wait()


    trial_counter = 0
    for rep in range(1, numRepetitions + 1):
        token_order = list(range(1, numTokens + 1))
        random.shuffle(token_order)  # Randomize the token sequence each time
        try:
            for i in token_order:
                trial_counter += 1
                print(f'trial_counter:{trial_counter}')
                # Drawing the target
                stimulus = vowel % (group, i)  # Stimulus is defined using formatted string
                print(f'stimulus:{stimulus}')
                

                if trial_counter == 1:
                    # LOAD THE BACKGROUND IMAGE:
                    #target_image_path = 'tokens.jpg'
                    # LOAD THE BACKGROUND IMAGE:

                    imageid = re.search(r'(.*_\w)\d*', stimulus).group(1)
                    print(f'imageid:{imageid}')
                    targetim = Image.open(os.path.join(BWD, f"{imageid}_tokens.jpg"))
                    targetim = np.array(targetim)
                    targetim = targetim / np.max(targetim)
                    originaltargetim=targetim
                    #sort out the image size for scaling and such
                    TargetImageSize = np.shape(targetim)
                    #what do we do to scale this properly? We have a screen
                    #size, and we will scale to the maximum dimension.
                    maxScale = min(TargetImageSize[1] / (ScreenSize[2] - ScreenSize[0]), TargetImageSize[0] / (ScreenSize[3] - ScreenSize[1]))
                    FBRadius = round((1 / maxScale) * FBRadius)

                    # Estimate the future size of the image on the screen
                    #TargetImageScaledSize = np.floor(maxScale * TargetImageSize[::-1])

                    # Cast into centered coordinates
                    ImageDisplaySize = np.array([0, 0, ScreenSize[2] - ScreenSize[0], ScreenSize[3] - ScreenSize[1]])

                    # ImageSize is the original size of the image
                    ImageSize = TargetImageSize[:2]



                    #size_x = targetim.size[0]
                    #size_y = targetim.size[1]
                    #targetim.size = [size_x * 0.3, size_y * 0.5]
    
                else:
                    # If it is not the first trial of the block, we should display the previous trial's feedback (if a response was recorded)
                    targetim = targetim_with_one_FB

                # Otherwise, it's already filled, with feedback, etc.
                #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=WarnTextCol)
                w = visual.ImageStim(window, image=targetim)  # Assuming target_image_path is the path to your target image
                # Use the ImageDisplaySize values
                size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                w.size = [size_x, size_y]
                w.draw()
                window.flip()
                event.waitKeys(0.5)
                w.autoDraw = False
                #window.close()

                # Load and play the target sound
                sound_path = os.path.join(BWD, f"{stimulus}.wav")
                print(f'sound_path:{sound_path}')
                # Create an instance of AudioRecorder
                audio_recorder = AudioRecorder()
                # Play the recorded audio from the file
                audio_recorder.play_audio(sound_path)
                #target_sound = sound.Sound(sound_path)
                #target_sound.play()

                # Display countdown
                #w = visual.ImageStim(window, image=targetim)
                #w = visual.TextStim(window, text="", pos=(0, 0), color=(-1, -1, -1), height=50)
                #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=WarnTextCol)
                for count in reversed(range(1, 4)):
                    w = visual.ImageStim(window, image=targetim)
                    size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                    size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                    w.size = [size_x, size_y]
                    w.draw()
                    window.flip()
                    event.waitKeys(0.5)
                    w.autoDraw = False

                    w = visual.TextStim(window, text="", pos=(0, 0), color=(-1, -1, -1), height=50)
                    #size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                    #size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                    #w.size = [size_x, size_y]
                    w.text = str(count)
                    w.font_size = 50
                    w.draw()
                    window.flip()
                    event.waitKeys(0.5)
                    w.autoDraw = False

                #window.close()
                # Set up audio recording parameters
                fs = 11000
                duration = RecordDuration
                #recorder = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype=np.int16)

                #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=WarnTextCol)
                # Visual feedback during recording
                #w = visual.ImageStim(window, image=targetim)
                #warn_text_col = [175, 175, 175]
                #targetim.draw()
                #window.flip()
                #event.waitKeys(2)
                w = visual.ImageStim(window, image=targetim)
                size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                w.size = [size_x, size_y]
                w.draw()
                window.flip()
                event.waitKeys(0.5)
                w.autoDraw = False

                w = visual.TextStim(window, text="!", pos=(0, 0), color=(-1, -1, -1), height=50)
                #w.draw()
                #window.flip()
                #event.waitKeys(RecordDuration)
                # Initialize an empty buffer to store the audio data
                #buffer = []

                # Start the audio stream with the callback function
                #with sd.InputStream(callback=callback, channels=1, samplerate=fs):
                # Create an instance of AudioRecorder
                audio_recorder = AudioRecorder()
                y = audio_recorder.record_audio(duration=RecordDuration, fs = fs, window = window, w = w)
                #w.draw()
                #window.flip()
                #event.waitKeys(RecordDuration)
                #w.autoDraw = False
                
                


                     # Keep the program running for the specified duration
                     #sd.sleep(int(duration * 1000))

                    # Concatenate the chunks in the buffer to get the full recording
                #y = np.concatenate(buffer, axis=0)
                #buffer.clear()

                # Save the full recording to a WAV file
                # Save the recorded audio to a WAV file
                out_wav = os.path.join(BWOD, f'Block_{block_number}_Condition_{condition_number}_{trial_counter:03}_{stimulus}_Repetition{rep:03}.wav')
                sf.write(out_wav, y, fs, subtype='PCM_16')
                audio_recorder.clear_buffer()

                #print("Recording saved as full_recording.wav")

                #sd.wait()
                #y = recorder.flatten()
                # Close PsychoPy window
                #window.close()

                
                if DEBUG == 2:
                    # Assuming 'stimulus' contains the filename without extension
                    filename = os.path.join(BWD, stimulus + '.wav')
                    recording, Fs = sf.read(filename, always_2d=True)
                    bits = recording.dtype.itemsize * 8
                    #RMS = 0.001
                else:
                    recording, Fs = sf.read(out_wav, always_2d=True)
                    bits = recording.dtype.itemsize * 8
                
                # Check RMS
                CheckRMS = rms(recording)
                print(f'CheckRMS:{CheckRMS}')
                core.wait(0.7)
                start_time, offset, onset_high, end_time, center = onset_offset(out_wav, 0)
                print(f'start_time:{start_time}, end_time:{end_time}, center{center}')
                if end_time-start_time <= 0.02:
                    print(f'duration:{end_time-start_time}')
                    CheckRMS = RMSIncrement*RMS

                if CheckRMS<=(RMSIncrement*RMS):
                    print('RMS is less than thershold value')
                    # if it wasn't loud enough, request louder response
                    #we redraw the screen incorporating only the previous
                    #production, and no new one
                    #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=WarnTextCol)
                    w = visual.ImageStim(window, image=targetim)
                    size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                    size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                    w.size = [size_x, size_y]
                    w.draw()
                    window.flip()
                    w.autoDraw = False
                    warning_text = 'No response was recorded.\n Please speak louder and longer when the "!" appears'
                    w = visual.TextStim(window, text=warning_text , pos=(0, 0), color=WarnTextCol, height=32)
                    w.draw()
                    window.flip()
                    event.waitKeys(3)
                    w.autoDraw = False
                    #output a null line
                    with open(fid, 'a') as file:
                        # Create a string in Python format
                        format_str = "{}\t{}\t{}\t{}\t{}\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN"

                        # Format the string with actual values
                        formatted_line = format_str.format(BlockNum, trial_counter, stimulus, rep, i)

                        # Write the formatted line to the file
                        file.write(formatted_line + '\n')
                    #We basically need to reset this for display purposes, the
                    #image that is written should be empty of feedback (since
                    #there wasn't any) and the image stored for next
                    #presentation should be feedback free as well
                    targetim =originaltargetim
                    file_name = f'Block_{block_number}_Condition_{condition_number}_{trial_counter}_{stimulus}_Repetition{rep}.jpg'
                    file_path = os.path.join(BWOD, file_name)
                    print('file_path:{file_path}')
                    # Save the image
                    #image = Image.fromarray(targetim)
                    imageio.imwrite(file_path,(targetim*255).astype(np.uint8))
                    targetim_with_one_FB=targetim
                    if NPersistFB > 1:
                        if persistent_feedback.shape[0] < NPersistFB:
                            persistent_feedback = np.vstack([persistent_feedback, [round(ScreenSize[0] / 2), round(ScreenSize[1] / 2)]])
                        else:
                            persistent_feedback = np.vstack([persistent_feedback[NPersistFB - 1:NPersistFB, :], [round(ScreenSize[0] / 2), round(ScreenSize[1] / 2)]])
                    else:
                        persistent_feedback = np.array([[round(ScreenSize[0] / 2), round(ScreenSize[1] / 2)]])
                    
                    PFBVALID=0
                    #window.close()
                else:
                    #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=WarnTextCol)
                    w = visual.ImageStim(window, image=targetim)
                    size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                    size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                    w.size = [size_x, size_y]
                    w.draw()
                    window.flip()
                    w.autoDraw = False
                    #window.close()
                    # Cut the recording to the middle portion
                    part_rec = recording[int(Fs * start_time):int(Fs * end_time)]
                    if DEBUG !=2:
                        part_rec = part_rec[int(Fs * TrimPortion[0]):int(len(part_rec) - Fs * TrimPortion[1])]
                    n_samples = len(part_rec)
                    Ncoeffs = int(2 + Fs / 1000) #11

                    # F0 estimate
                    son = hamming(n_samples) * part_rec
                    cn1 = lfilter([1], [1, 0.63], son)
                    LF = int(np.floor(Fs / 500))
                    HF = int(np.floor(Fs / 70))
                    cn = cn1[LF:HF]
                    ind = np.argmax(cn)
                    mx_cep = cn.flatten()[ind]
                    f0 = Fs / (LF + ind)

                    if f0 >= 350:
                        f0 = 200
                    
                    #formants=np.zeros((3,1))

                    #------Grab the middle portion and analyse it

                    df = int(0.05*Fs)
                    if len(part_rec) < 2200: # if the length of the cut portion is less than 200 ms, then take 20 ms segment
                        df = int(0.01*Fs)

                    if len(part_rec) < 550:
                        df = int(0.005*Fs)
                    
                    end_index = len(part_rec) // 2
                    sound1 = part_rec[end_index - df : end_index + df + 1]
                    sound2 = sound1.flatten() * hamming(len(sound1))
                    preemph = [1, 0.63]
                    sound2 = lfilter([1], preemph, sound2)

                    # Calculate LPC coefficients
                    a= librosa.core.lpc(sound2, order= Ncoeffs)
                    f1mean, f2mean, f3mean = frmnts(a, Fs)

                    # check extreme values
                    if f1mean < 300:
                        f1mean=f2mean
                        f2mean=f3mean
                    if f2mean < 1500:
                        f2mean=f3mean
                        f3mean=None
                    
                    #scaling
                
                    F1_F0=f1mean-f0
                    F2_F0=f2mean-f0

                    with open(fid, 'a') as file:
                        format_str = "{}\t{}\t{}\t{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}"

                        # Format the string with actual values
                        formatted_line = format_str.format(BlockNum, trial_counter, stimulus, rep, i, f0, f1mean, f2mean, f3mean, F1_F0, F2_F0, start_time, end_time, center)

                        # Write the formatted line to the file
                        file.write(formatted_line + '\n')
                    #reload the original image with no feedback
                    targetim=originaltargetim #This is inefficient but I think trying to store
                    #and repeatedly update the images is too complicated for now it
                    #may even be possible to make this save before updating with
                    #the feedback...
                    XPosition = round((F2_F0 - FeedbackScale[0, 0]) / (FeedbackScale[1, 0] - FeedbackScale[0, 0]) * ImageSize[1])
                    # NOTICE THAT: order of subtraction is flipped because the axis is backwards, i.e., 6 is at the bottom, -1 is at the top
                    YPosition = ImageSize[0] - round((F1_F0 - FeedbackScale[0, 1]) / (FeedbackScale[1, 1] - FeedbackScale[0, 1]) * ImageSize[0])

                    #CATCH if positions are -ve (because this will crash) or
                    #out of range because this will also crash
                    if any([XPosition < (1 + FBRadius), XPosition > (ImageSize[1] - FBRadius), YPosition > (ImageSize[0] - FBRadius)]):
                        # So, for the case where feedback is out-of-range...
                        # find out which it is
                        if XPosition <= 0 + FBRadius:
                            XPosition = 1 + FBRadius
                        if YPosition <= 0 + FBRadius:
                            YPosition = 1 + FBRadius
                        if XPosition >= (ImageSize[1] - FBRadius):
                            XPosition = (ImageSize[1] - (1 + FBRadius))
                        if YPosition >= (ImageSize[0] - FBRadius):
                            YPosition = (ImageSize[0] - (1 + FBRadius))
                    # Assuming YPosition, XPosition, and FBRadius are floats or other numeric types
                    YPosition = int(YPosition)
                    XPosition = int(XPosition)
                    FBRadius = int(FBRadius)

                    # Now you can use these variables in your slicing operations
                    targetim[YPosition - FBRadius:YPosition + FBRadius, XPosition - FBRadius:XPosition + FBRadius, 0] = 0
                    targetim[YPosition - FBRadius:YPosition + FBRadius, XPosition - FBRadius:XPosition + FBRadius, 1] = 175
                    targetim[YPosition - FBRadius:YPosition + FBRadius, XPosition - FBRadius:XPosition + FBRadius, 2] = 255
                    targetim_with_one_FB=targetim
                    print(targetim_with_one_FB[YPosition - FBRadius:YPosition + FBRadius, XPosition - FBRadius:XPosition + FBRadius, 0])
                    print(targetim_with_one_FB[YPosition - FBRadius:YPosition + FBRadius, XPosition - FBRadius:XPosition + FBRadius, 1])
                    print(targetim_with_one_FB[YPosition - FBRadius:YPosition + FBRadius, XPosition - FBRadius:XPosition + FBRadius, 2])

                    # Define the filename using the provided format
                    filename = f"Block_{block_number}_Condition_{condition_number}_{trial_counter}_{stimulus}_Repetition{rep}.jpg"

                    # Save the image to the specified path
                    file_path = os.path.join(BWOD, filename)
                    #image = Image.fromarray(targetim)
                    imageio.imwrite(file_path,(targetim).astype(np.uint8))
                    for rgb in range(3):
                        targetim[YPosition - FBRadius:YPosition + FBRadius, XPosition - FBRadius:XPosition + FBRadius, rgb] = PFB_Col[-1][rgb]
                    
                    # Fill in the persistent feedback
                    if persistent_feedback.shape[0] != 0:
                        for PFB in range(persistent_feedback.shape[0]):
                        # Next check if the previous trial contained a valid response
                            if PFB == persistent_feedback.shape[0] - 1 and PFBVALID == 1:
                                # Adjust indices according to Python's zero-based indexing
                                targetim[
                                    int(persistent_feedback[PFB, 0] - FBRadius) : int(persistent_feedback[PFB, 0] + FBRadius + 1),
                                    int(persistent_feedback[PFB, 1] - FBRadius) : int(persistent_feedback[PFB, 1] + FBRadius + 1),
                                    :
                                    ] = PFB_Col[PFB, 0]
                    #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=WarnTextCol)
                    w = visual.ImageStim(window, image=targetim)
                    size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                    size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                    w.size = [size_x, size_y]
                    w.draw()
                    window.flip()
                    event.waitKeys(1.5)
                    w.autoDraw = False
                    #window.close()
                    # fill the array of persistent feedback values:
                    if NPersistFB > 1:
                        if persistent_feedback.shape[0] < NPersistFB:
                            persistent_feedback = np.vstack([persistent_feedback, [YPosition, XPosition]])
                        else:
                            persistent_feedback = np.vstack([persistent_feedback[NPersistFB - 1 : NPersistFB, :], [YPosition, XPosition]])
                    elif NPersistFB == 1:
                        persistent_feedback = np.array([[YPosition, XPosition]])
                    else:
                        # Handle the case when NPersistFB is less than or equal to 0
                        pass
                    PFBVALID = 1
                #window = visual.Window(size=(800, 800), units='pix', fullscr=False, color=WarnTextCol)
                w = visual.ImageStim(window, image=targetim)
                size_x = ImageDisplaySize[2] - ImageDisplaySize[0]
                size_y = ImageDisplaySize[3] - ImageDisplaySize[1]
                w.size = [size_x, size_y]
                w.draw()
                window.flip()
                w.autoDraw = False
                w = visual.TextStim(window, text='+' , pos=(0, 0), color=(-1, -1, -1), height=50)
                w.draw()
                window.flip()
                event.waitKeys(3)
                w.autoDraw = False
                #window.close()
        except Exception as e:
            traceback.print_exc()  