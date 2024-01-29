import os
from pathlib import Path
import numpy as np
from psychopy import visual, core, event, sound, monitors
from runCond import runCond
#from utils import rms, callback, frmnts, onset_offset

def training_eeg(nsubj, session, group, nblocks=5):
    '''
    this function requires the following input:
    subject number: any number
    session number: any number (but it will be 1,2, or 3
    group: 'H' or 'L'
    OPTIONAL INPUT: nblocks a number. I added this because you will want
    different numbers of blocks since the sessions will be of different
    lengths. It will default to 5 if no input is specified here.
    Calling the funciton is done as follows:
    expe(subjectnumber,sessionnumber,group,nblocks); e.g. expe(1,2,'H',8)
    For ease of calculation 1 block is 30 * 2 trials = 60 trials @
    approximately 5s each = 5 mins
    therefore in a 60minute session, you can set this to 11 or 12 Blocks
    '''
    DEBUG = 0 #If debug is set to 1 this ensures small screen for access to
    #python window, if debug is set to 2 this tests the lpc by feeding the
    #source vowel back into the mechanism and displaying its formants in the
    #space (this is a sanity to check to ensure that the lpc and display
    #scaling are correct)
    
    numRepetitions = 1 # Number of repetitions of each token within a block. Default is 1
    numTokens = 90 # Number of tokens per "condition" (condition is a VOWEL)
    conditions = ['A%s_a%d', 'E%s_e%d'] # these must be the filename prefixes
    NPersistFB = 1 # How many previous trials should be displayed?
    TrimPortion = [0.01, 0.01] # How much sound, in seconds, to cut off the front and back of the sound for analysis purposes
    ScreenScaleFactor = 1 # How much of the screen to use. Factors <1 will use proportion of screen, centred.
    HamWind = 1 # For example. The number of windows to use when calculating the LPC, 1 may be sufficient.
    RecordDuration = 1 #Specify the duration of the recording in seconds, here
    RMS = 0.001
    RMSIncrement = 1 #Specify a minimum volume level for the record, relative to a 5s recording of the background noise level carried out at the beginning of the experiment
    FeedBackRadius = 5 #How big should the feedback square be? 5 was the previous standard value. This is scaled later to take up the desired number of pixels
    #specify the scaling for the Bark transform
    FeedbackScale = np.array([[2600, 650], [600, 50]]) #The X-start Y-start; X-end Y-end co-ordinates, these axes([600 2600 50 650])were used to draw feedback image
    FeedbackAxes = np.abs(np.subtract(FeedbackScale[0], FeedbackScale[1]))
    #script_path = os.path.abspath(__file__)
    #basepath, _ = os.path.split(script_path)

    basepath = Path(os.path.realpath("")).as_posix()
    bwod = os.path.join(basepath, 'Results')
    BWD = os.path.join(basepath, 'Sources') #where are the sound files and the images?
    SUBJECT_DIR = os.path.join(bwod, f'Subject_{nsubj}')
    
    nsubj_str = str(nsubj)
    session_str = str(session)
    SUBJECT_DIR = os.path.join(bwod, f'Subject_{nsubj_str}')
    SESSION_DIR = os.path.join(SUBJECT_DIR, f'Session_{session_str}')

    # Create the SUBJECT_DIR and SESSION_DIR if they don't exist
    os.makedirs(SUBJECT_DIR, exist_ok=True)
    os.makedirs(SESSION_DIR, exist_ok=True)

    filename = f'Subject_{nsubj_str}_{group}_Session_{session_str}_Results.txt'
    fid = os.path.join(SESSION_DIR, filename)

    with open(fid, 'w') as file:
        file.write('BlockNumber\tTrialNumber\tVowelID\tInstance\tTokenNum\tF0\tF1\tF2\tF3\tF1_F0\tF2_F0\tOnset\tOffset\tCenter\n')
    
    # Set some parameters
    whichScreen = 0
    ScreenScaleFactor = 0.5 if DEBUG > 0 else 1.0

    # Get screen resolution
    
    mon = monitors.Monitor("testMonitor")  # Replace "testMonitor" with the actual monitor name
    mon.setWidth(34)  # adjust the width with the actual monitor width (in cm)

    # Get the screen resolution
    resolution = mon.getSizePix()
    xorig = round((resolution[0] - (ScreenScaleFactor * resolution[0])) * ScreenScaleFactor)
    yorig = round((resolution[1] - (ScreenScaleFactor * resolution[1])) * ScreenScaleFactor)
    ScreenSize = [xorig, yorig, xorig + (ScreenScaleFactor * resolution[0]), yorig + (ScreenScaleFactor * resolution[1])]
    # Set up psychopy window
    # Create a window
    window = visual.Window(size=(ScreenSize[2] - ScreenSize[0], ScreenSize[3] - ScreenSize[1]), units='pix', screen=whichScreen, fullscr=False, color=[255,255,255])
    # Get baseline RMS

    #RMS = get_baseline_rms(window, SESSION_DIR)

    # Display text
    #text = visual.TextStim(win, text='Hola: Tienes que repetir el sonido cuando el signo ! aparece', pos=(0, 0), color=[50, 50, 50], height=36)
    w = visual.TextStim(window, text='Hello: You have to repeat the sound when the sign ! appears' , pos=(0, 0), color=(-1, -1, -1), height=50)
    w.draw()
    window.flip()

    # Wait for 5 seconds
    event.waitKeys(5)

    # Close the window
    #window.close()

    for k in range(1, nblocks + 1):
        print(f'nblock:{k}')
        numbcond = np.random.permutation(len(conditions)) #generate random vowel order for every block
        print(f'condition:{numbcond}')
        #window2 = visual.Window(size=(ScreenSize[2] - ScreenSize[0], ScreenSize[3] - ScreenSize[1]), units='pix', fullscr=False, color=[255,255,255])
        # Set text size and draw text
        w = visual.TextStim(window, text='The beginning of the block', pos=(0, 0), color=(-1, -1, -1), height=32)
        w.draw()
        # Flip the window
        window.flip()
        # Wait for 2 seconds
        event.waitKeys(2)
        for v in numbcond:
            print(f'nvowel:{v}')
            vowel = conditions[v]
            runCond(nsubj, k, group, vowel, numRepetitions, numTokens, BWD, SESSION_DIR, fid,
                    NPersistFB, TrimPortion, HamWind, RecordDuration, ScreenSize, whichScreen, window, FeedbackAxes, FeedbackScale,
                    0.001, RMS, RMSIncrement, v, FeedBackRadius, DEBUG) #vowel must be the prefix in the filename

            # Display transition message
            w = visual.TextStim(window, text='Now we move on to the other vowel', pos=(0, 0), color=(-1, -1, -1), height=30)
            w.draw()
            window.flip()
            event.waitKeys(5)
            #window.close()
            for counter in range(5, -1, -1):
                w = visual.TextStim(window, text=str(counter), pos=(0, 0), color=(-1, -1, -1), height=36)
                w.draw()
                window.flip()
                event.waitKeys(1)
                #window.close()


        # Display pause message
        w = visual.TextStim(window, text='You can pause now\nPress the ENTER key to continue', pos=(0, 0), color=(-1, -1, -1), height=36)
        w.draw()
        window.flip()
        event.waitKeys(1)
        #window.close()

    # Display end of training message
    w = visual.TextStim(window, text='The training is over', pos=(0, 0), color=(-1, -1, -1), height=32)
    w.draw()
    window.flip()
    event.waitKeys(1)
    window.close()



if __name__ == "__main__":
    # Set your parameters for the function call
    nsubj = 1
    session = 1
    group = 'H'
    nblocks = 1

    training_eeg(nsubj, session, group, nblocks)
