# Text-to-Speech_Generator
### Overview
This text to speech generator reads the text_to_speech.txt file and is run from main.py. The other two files, NLP.py and SpeechGenerator.py are imported in main.py. This generator can convert most text to speech including dates, fractions, and abbreviations.
### Setup
Several python packages that need to be downloaded were used for this generator including, but not limited to; __nltk, pathlib, re, num2words, numpy, pyaudio, wave, math, random, and os.__
Installation of these packages are necessary in order for the generator to work properly. 
### NLP
NLP.py contains the NLP class which has seven built in functions four of which are helper functions. The __init__ function initializes the NLP object, and if the file text_to_speech.txt is found, converts the text found there. Otherwise the user will be prompted to enter text manually or enter a URL for a website to be transcribed and read. After input is collected the __init__ function calls the functions, structure_analyzer and text_normalizer which generates information tokens enclosed in "<>" and converts sybols, numbers, and special text to english words.

**Note: URL transcription, will sometimes try to read hidden data.

**Note: Contractions will crash the program, avoid words like I've, would've, I'd.
### Speech Generator
SpeechGenerator.py contains the SG class which is created using a list of words and tokens generated by the NLP class and has 3 functions. The __init__ function assigns data, and calls the functions, text_to_phoneme and prosody_analyzer which create phonemes based on the words given and then couples them to create diphones. Tokens are converted into pauses or passed on for sentence type generation, i.e. exclamation, question, regular.
### Output
 The output of running the main function should be the printed diphones and remaining information tokens, a message that says "Playing..." when the audio begins and a message that says "Stopped playing" when the audio finishes.
 
 **Note: Because of the way build_d, a function within SpeechGenerator.py, simulates inflection and volume, you may recieve several "Playing..." and "Stopped playing" messages.
