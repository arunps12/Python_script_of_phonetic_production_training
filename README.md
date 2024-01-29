The function names training_eeg can be use for phonetic production training with different types of visual feedback.
This function requires the following input:
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



DEBUG=0;%If debug is set to 1 this ensures small screen for access to
%matlab window, if debug is set to 2 this tests the lpc by feeding the
%source vowel back into the mechanism and displaying its formants in the
%space (this is a sanity to check to ensure that the lpc and display
%scaling are correct)
