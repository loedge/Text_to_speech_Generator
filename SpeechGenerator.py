"""
Text-to-phoneme converter:  convert the tokens in the spoken text to pronunciation tokens which will be a sequence of
phonemes

Prosody analyzer: add additional factors to the data set such as pitch, timing, speaking rate, and emphasis
These aspects of a language separate robotic flat speech to a more natural fluid speech, include crossfades,
accounting for unwanted pauses and abruptly starting sounds

Waveform producer: take all the information generated and create the waveforms required for each token, create the
output for the inputted text.

"""
from nltk.stem.porter import *
from nltk.corpus import cmudict
import sound_dict_generator
import numpy as np

class SG:
    normalized_words = []
    pronunciation_tokens = []
    post_prosody = []
    cmud = cmudict.dict()
    sound_dict = sound_dict_generator.Synth().diphones

    # THIS IS USED FOR TESTING
    #def __init__(self):
        #self.normalized_words = ['<beginning>', '<question>', 'hello', 'there', 'professor', '<break,comma,1>', 'how', 'are',
        #                         'you', 'doing', '<break,question,2>', 'i', 'am', 'good', '<break,sent_end,2>',
        #                         '<exclamation>', 'This', 'is', 'so', 'amazing', '<break,exclamation,2>', '<end>']
        # self.normalized_words = ['doctor', 'rabbits', 'email', 'is', 'i', 'l', 'u', 'v', 'c', 'a', 'r' 'r',
        # 'o' 't' 's', 'three', 'zero', 'five', 'at', 'g', 'mail', 'dot', 'c', 'o', 'm', '<break,sent_end,2>', 'you',
        # 'can', 'checkout', 'his', 'website', '<break,comma,1>', 'r', 'a', 'b', 'b', 'i', 't', 'd', 'r', 'dot', 'g',
        # 'o', 'v', '<break,sent_end,2>', 'he', 'uses', 'forty', 'milliliters', 'beakers', 'to', 'find', 'tilde',
        # 'volume', '<break,sent_end,2>', 'he', 'has', '<currency>', 'negative', 'three', 'dollars', 'in', 'his',
        # 'bank', 'account', '<break,sent_end,2>']

    def __init__(self, n_w: list):
        self.normalized_words = n_w
        self.text_to_phoneme()
        self.prosody_analyzer()

    def text_to_phoneme(self):
        skip = 0
        for w in self.normalized_words:  # get the token from normalized_words
            if w in self.cmud:
                phone = self.cmud[w][0]  # convert tokens to its phoneme form
                for i in range(len(phone)):
                    phone[i] = re.sub("[^a-zA-Z\\s\-]", "", phone[i]).lower()
                self.pronunciation_tokens.append(phone)  # add the phoneme form of the word to pronunciation_tokens
            elif w[0] == '<' and w[-1] == '>':
                self.pronunciation_tokens.append([w])
            else:
                for i in range(len(w)):
                    if skip > 0:
                        skip -= 1
                        continue
                    try:
                        phone = self.cmud[w[i:i+5].lower()][0]
                        skip = 4
                    except:
                        try:
                            phone = self.cmud[w[i:i+4].lower()][0]
                            skip = 3
                        except:
                            try:
                                phone = self.cmud[w[i:i+3].lower()][0]
                                skip = 2
                            except:
                                try:
                                    phone = self.cmud[w[i:i+2].lower()][0]
                                    skip = 1
                                except:
                                    try:
                                        phone = self.cmud[w[i].lower()][0]
                                    except:
                                        pass
                    for i in range(len(phone)):
                        phone[i] = re.sub("[^a-zA-Z\\s\-]", "", phone[i]).lower()
                    self.pronunciation_tokens.append(phone)
                # TODO: figure out what to do with words not in the cmu dictonary
                #       Possibilities: should we get the root?, use the google converter?


    def prosody_analyzer(self):
        temp = []
        for w in self.pronunciation_tokens:
            if w[0] == "<beginning>" or w[0] == "<end>":
                temp.append('pau')
                if w[0] == "<end>":
                    temp.append(w[0])
            elif w[0] == "<break,comma,1>":
                temp.append('pau')
                temp.append('pau')
            elif w[0] == "<break,semicolon,1.5>" or w[0] == "<break,colon,1.5>":
                temp.append('pau')
                temp.append('pau')
                temp.append('pau')
            elif w[0] == "<break,sent_end,2>" or w[0] == "<break,question,2>" or w[0] == "<break,exclamation,2>":
                temp.append('pau')
                temp.append('pau')
                temp.append(w[0])
                temp.append('pau')
            elif w[0] == "<question>" or w[0] == "<exclamation>":
                temp.append(w[0])
            elif w[0] == "<space>":
                continue
            else:
                for p in w:
                    temp.append(p)
        for i in range(len(temp)):
            if temp[i] == "<exclamation>" or temp[i] == "<question>" or temp[i] == "<break,sent_end,2>" or temp[i] == "<break,question,2>" or temp[i] == "<break,exclamation,2>":
                self.post_prosody.append(temp[i])
                continue
            if i != len(temp)-1:
                if temp[i+1] == "<exclamation>" or temp[i+1] == "<question>" or temp[i+1] == "<break,sent_end,2>" or temp[i+1] == "<break,question,2>" or temp[i+1] == "<break,exclamation,2>" or temp[i+1] == "<end>":
                    if temp[i+1] == "<end>":
                        self.post_prosody.append(temp[i+1])
                    else:
                        self.post_prosody.append(temp[i] + '-' + temp[i + 2])
                else:
                    self.post_prosody.append(temp[i] + '-' + temp[i+1])
        print(self.post_prosody)

        # TODO: add the additional factors to the sounds to create normal sounding speech
        #  in the sound_dict there are different pause times based on the type of pause it is - the issue is that in the
        #  diphones folder there is only one pause-phoneme length for each phoneme so if we can figure out some way to
        #  change that that would make it sound a lot better

        # TODO: add additional factors to the data set such as pitch, timing, speaking rate, and emphasis
        #  there are sentence tags at the beginning of sentences ending with ! and ? so finding a way to manipulate the
        #  sounds with factors (pitch, timing, speaking rate, emphasis) based on that would help a lot too

        # TODO: currently theres no contingency for when the prosody_analyzer encounters the beginning sentence tags
        #  for ! and ?, should they be left in and the tone dealt with in build_d()??


def build_d(p_t_c: SG):
    sound_dict = sound_dict_generator.Synth().diphones
    p_t = p_t_c.post_prosody
    temp = []
    temps = sound_dict_generator.sound_dict(rate=16000)
    flag = False
    flag2 = False
    for w in p_t:
        if w == "<exclamation>" or flag:
            flag = True
            if w == "<break,exclamation,2>":
                flag = False
                temps.data = temp.astype(np.int16)
                temps.change_speed(1.08)
                temps.rescale(0.95)
                temps.play()
                temp = []
            try:
                temp = np.append(temp, (sound_dict[w]))
            except:
                pass
        elif w == "<question>" or flag2:
            flag2 = True
            if w == "<break,question,2>":
                flag2 = False
                temps.data = temp.astype(np.int16)
                temps.change_speed(1.04)
                temps.rescale(0.7)
                temps.play()
                temp = []
            try:
                temp = np.append(temp, (sound_dict[w]))
            except:
                pass
        else:
            if w == "<break,sent_end,2>" or w == "<end>":
                temps.data = temp.astype(np.int16)
                temps.change_speed(1.04)
                temps.rescale(0.5)
                temps.play()
                temp = []
            try:
                temp = np.append(temp, (sound_dict[w]))
            except:
                pass

