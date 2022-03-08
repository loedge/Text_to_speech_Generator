import NLP
import SpeechGenerator

if __name__ == '__main__':
    c = NLP.NLP()
    words = c.normalized_words
    talk = SpeechGenerator.SG(words)
    SpeechGenerator.build_d(talk)


