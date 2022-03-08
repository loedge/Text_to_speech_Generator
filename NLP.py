import nltk
import pathlib
from urllib import request
import re
from num2words import num2words


class NLP:
    words = []
    structured_words = []
    normalized_words = []

    def __init__(self):
        if pathlib.Path("text_to_speech.txt").exists():
            with open("text_to_speech.txt", "r") as text:
                some_text = text.read()
        else:
            option = input("How would you like to input the text? \n A) Through a URL \n B) By typing it in \n")
            print(option)
            if option.lower() == "a":
                url = ''
                url = input("Please enter the url of the website you want spoken.\n")
                lines = ''
                try:
                    response = request.urlopen(url)
                    raw = response.read().decode('utf8')
                except request.HTTPError as exception:
                    print(exception)
                for i in range(len(raw)):
                    if i + 1 >= len(raw):
                        continue
                    if raw[i] == ">" and raw[i + 1] != "<" and raw[i + 1] != ".":
                        if raw[i - 7:i] == "<script":
                            continue
                        elif raw[i - 6:i] == "<style":
                            continue
                        act = ''
                        for j in range(len(raw)):
                            if i + j + 1 >= len(raw):
                                break
                            act = act + raw[i + j + 1]
                            if act[j] == '<':
                                act = act[:len(act) - 1]
                                break
                        lines = lines + act
                some_text = lines
            elif option.lower() == "b":
                some_text = input("Please enter the text you would like converted to speech. End the input with a period.\n")

        self.words = nltk.word_tokenize(some_text)
        self.structure_analyzer()
        self.text_normalizer()

    def structure_analyzer(self):
        # TODO: 1:30 - 2:30 change '-' to 'to'

        p = re.compile('([A-Z]\.)+[A-Z]')
        skip_tag = False
        prev_punc = False
        for i in range(len(self.words)):
            if i == 0:
                self.structured_words.append('<beginning>')
            elif i != 0 and not prev_punc:
                self.structured_words.append('<space>')
            elif i != 0 and prev_punc:
                prev_punc = False
            if skip_tag is False:
                if self.words[i] == '.':
                    if p.match(self.structured_words[-1]):
                        temp1 = self.structured_words[-1]
                        temp2 = temp1.replace('.', ' ')
                        temp3 = nltk.word_tokenize(temp2)
                        self.structured_words.pop()
                        for w in temp3: self.structured_words.append(w)
                        if i + 1 == len(self.words) or self.words[i + 1].isupper():
                            self.structured_words.append('<break,sent_end,2>')
                        # TODO: account for abbreviations not just acronyms - what did i mean by this
                    else:
                        self.structured_words.pop()
                        self.structured_words.append('<break,sent_end,2>')
                        prev_punc = True
                elif self.words[i] == '?':
                    for j in range(len(self.structured_words) - 1, 0, -1):
                        if self.structured_words[j][:2] == '<b':
                            self.structured_words.insert(j + 1, "<question>")
                            break
                    self.structured_words.pop()
                    self.structured_words.append('<break,question,2>')
                    prev_punc = True
                elif self.words[i] == '!':
                    for j in range(len(self.structured_words) - 1, 0, -1):
                        if self.structured_words[j][-2:] == '2>':
                            self.structured_words.insert(j + 1, "<exclamation>")
                            break
                    self.structured_words.pop()
                    self.structured_words.append('<break,exclamation,2>')
                    prev_punc = True
                elif self.words[i] == ',':
                    self.structured_words.pop()
                    self.structured_words.append('<break,comma,1>')
                    prev_punc = True
                elif self.words[i] == ';':
                    self.structured_words.pop()
                    self.structured_words.append('<break,semicolon,1.5>')
                    prev_punc = True
                elif self.words[i] == ':':
                    self.structured_words.pop()
                    self.structured_words.append('<break,colon,1.5>')
                    prev_punc = True
                elif self.words[i][0] == "'":
                    del self.structured_words[-1]
                    new_str = self.words[i - 1] + self.words[i]
                    self.structured_words.append(new_str)
                elif self.words[i][0] == "$":
                    self.structured_words.append('<currency>')  # should we have an currency tag
                    new_str = self.words[i] + self.words[i + 1]
                    self.structured_words.append(new_str)
                    skip_tag = True
                elif self.words[i][0] == "%":
                    del self.structured_words[-1]
                    new_str = self.words[i - 1] + self.words[i]
                    self.structured_words.append('<percentage>')  # should we have an percentage tag
                    self.structured_words.append(new_str)
                # TODO: should the tilde be at any point or only beginning and end
                elif self.words[i][0] == "~":
                    self.structured_words.append(self.words[i][0])
                    self.structured_words.append(self.words[i][1:])
                elif self.words[i][-1] == "~":
                    self.structured_words.append(self.words[i][:len(self.words[i] - 1)])
                    self.structured_words.append(self.words[i][-1])
                elif any(char.isalpha() for char in self.words[i][0]):
                    mark = False
                    for j in range(len(self.words[i])):
                        if self.words[i][j] == "-":
                            temp1 = self.words[i][:j]
                            temp2 = self.words[i][j+1:]
                            self.structured_words.append(temp1)
                            self.structured_words.append(temp2)
                            mark = True
                            break
                    if not mark:
                        self.structured_words.append(self.words[i])
                else:
                    self.structured_words.append(self.words[i])
            else:
                skip_tag = False

            if i == len(self.words) - 1:
                self.structured_words.append('<end>')

    def text_normalizer(self):
        comp_symbol_dict = {
            # TODO: add any more symbols
            # TODO: look for a way to distinguish if it is one instance of an symbol or another # (pound, number, hastag)
            '~': ['tilde'],
            '#': ['pound'],  # can be hashtag and number too
            '"': ['quote'],
            '<': ['less', 'then'],
            '>': ['greater', 'than'],
            '+': ['plus'],
            '(': ['open', 'parenthesis'],
            ')': ['closed', 'parenthesis'],
            '@': ['at'],
            '&': ['and'],
            '[': ['open', 'bracket'],
            ']': ['closed', 'bracket'],
            '=': ['equals'],
            '*': ['times'],
            '-': ['dash']
        }
        abbreviations = {
            # TODO: add more abbreviations to the list
            # TODO: look for a way to distinguish if it is one instance of an abreviaiton or another St. (street, saint)
            # TODO: figure out something to do with the periods so we dont have to have repeats
            'Dr': ['doctor'],
            'Dr.': ['doctor'],
            'mr': ['mister'],
            'mr.': ['mister'],
            'mrs': ['misses'],
            'mrs.': ['misses'],
            'ms': ['miss'],
            'ms.': ['miss'],
            'St': ['street'],  # or saint
            'St.': ['street'],  # or saint
            'etc': ['et', 'cetera'],
            'lbs': ['pounds'],
            'ft': ['feet'],
            'yd': ['yard'],
            'mi': ['mile'],
            'mm': ['millimeters'],
            'cm': ['centimeters'],
            'dm': ['decimeters'],
            'm': ['meters'],
            'dam': ['dekameters'],
            'hm': ['hectometers'],
            'km': ['kilometers'],
            'mL': ['milliliters'],
            'cL': ['centiliters'],
            'dL': ['deciliters'],
            # 'L': ['liters'],  # is this a thing?
            'daL': ['dekaliters'],
            'hL': ['hectoliters'],
            'kL': ['kiloliters'],
            'mg': ['milligrams'],
            'cg': ['centigrams'],
            'dg': ['decigrams'],
            'g': ['grams'],
            'dag': ['dekagrams'],
            'hg': ['hectograms'],
            'kg': ['kilograms'],
            'vol': ['volume'],
            'vs': ['versus'],
            # https://github.com/philgooch/abbreviation-extraction

        }
        TLD_dict = {
            # TODO: add some more TLDs
            '.com': ['dot', 'com'],
            '.gov': ['dot', 'gov'],
            '.net': ['dot', 'n', 'e', 't'],
            '.edu': ['dot', 'e', 'd', 'u'],
            '.de': ['dot', 'd', 'e'],
            '.icu': ['dot', 'i', 'c', 'u'],
            '.uk': ['dot', 'u', 'k'],
            '.ru': ['dot', 'r', 'u'],
            '.info': ['dot', 'info'],
            '.top': ['dot', 'top'],
            '.xyz': ['dot', 'x', 'y', 'z'],
            '.tk': ['dot', 't', 'k'],
            '.cn': ['dot', 'c', 'n'],
            '.ga': ['dot', 'g', 'a'],
            '.cf': ['dot', 'c', 'f'],
            '.nl': ['dot', 'n', 'l'],
        }  # top level domain
        emails = {
            # TODO: add some more emails
            'gmail': ['g', 'mail'],
            'yahoo': ['ya', 'hoo'],
            'comcast': ['com', 'cast']
        }
        for i in range(len(self.structured_words)):
            if self.structured_words[i][-4:] in TLD_dict:
                if self.structured_words[i][:len(self.structured_words[i]) - 4] in emails:
                    for w in emails.get(
                            self.structured_words[i][:len(self.structured_words[i]) - 4]): self.normalized_words.append(
                        w.lower())
                else:
                    for c in self.structured_words[i][:len(self.structured_words[i]) - 4]: self.normalized_words.append(
                        c.lower())
                for w in TLD_dict.get(self.structured_words[i][-4:]): self.normalized_words.append(w.lower())
            elif any(char.isdigit() for char in self.structured_words[i]) and self.structured_words[i][0] != "<":
                new_words = self.num_to_words(self.structured_words[i])
                # TODO: dates
                for w in new_words:
                    self.normalized_words.append(w.lower())
            elif self.structured_words[i] in abbreviations:
                # TODO: Abbreviations issues: the decimal, what if they are squared
                for w in abbreviations.get(self.structured_words[i]): self.normalized_words.append(w.lower())
            elif self.structured_words[i] in comp_symbol_dict:
                for w in comp_symbol_dict.get(self.structured_words[i]): self.normalized_words.append(w.lower())
            # TODO: Strech goals- chemical symbols, greek symbols
            else:
                self.normalized_words.append((self.structured_words[i]).lower())

    def num_to_words(self, word: str):
        temp_word = ''
        new_words = []
        if any(char == "-" for char in word):  # if - is before the first digit character
            new_words.append('negative')
            word = word.replace('-', '')

        if any(char == "$" for char in word):
            new_words = new_words + self.money_to_words(word)
        elif any(char == ":" for char in word):
            new_words = new_words + self.time_to_words(word)
            # TODO: account for ratios
            #  check by if the next word is AM/PM if it is then its time if not then its ratio
            #  issue of military time with that
            # completed in time_to_word!
        elif any(char == "%" for char in word):
            new_words = new_words + self.percent_to_words(word)
        elif any(char == "/" for char in word):
            count = 0
            date = False
            for char in word:
                if char == "/":
                    count += 1
                if count == 2:
                    date = True
            if date:
                month = True
                day = False
                days = 0
                year = False
                years = 0
                for i in range(len(word)):
                    if year:
                        years += 1
                    if i == len(word) - 1:
                        if years == 2:
                            if int(word[-years:]) > 21:
                                new_words.append('nine')
                                new_words.append('teen')
                                temp1 = num2words(word[-years:])
                                temp2 = temp1.replace('-', ' ')
                                temp3 = nltk.word_tokenize(temp2)
                                for w in temp3: new_words.append(w)
                            else:
                                new_words.append('twenty')
                                temp1 = num2words(word[-years:])
                                temp2 = temp1.replace('-', ' ')
                                temp3 = nltk.word_tokenize(temp2)
                                for w in temp3: new_words.append(w)
                        elif years == 4:
                            temp1 = num2words(word[-years:-(years-2)])
                            temp2 = temp1.replace('-', ' ')
                            temp3 = nltk.word_tokenize(temp2)
                            for w in temp3: new_words.append(w)
                            temp1 = num2words(word[-(years-2):])
                            temp2 = temp1.replace('-', ' ')
                            temp3 = nltk.word_tokenize(temp2)
                            for w in temp3: new_words.append(w)
                    if word[i] == "/" and day:
                        temp1 = num2words(word[i-days:i], to='ordinal')
                        temp2 = temp1.replace('-', ' ')
                        temp3 = nltk.word_tokenize(temp2)
                        for w in temp3: new_words.append(w)
                        days = False
                        year = True
                    if day:
                        days += 1
                    if word[i] == "/" and month:
                        if word[:i] == "1" or word[:i] == "01":
                            new_words.append("january")
                        elif word[:i] == "2" or word[:i] == "02":
                            new_words.append("february")
                        elif word[:i] == "3" or word[:i] == "03":
                            new_words.append("march")
                        elif word[:i] == "4" or word[:i] == "04":
                            new_words.append("april")
                        elif word[:i] == "5" or word[:i] == "05":
                            new_words.append("may")
                        elif word[:i] == "6" or word[:i] == "06":
                            new_words.append("june")
                        elif word[:i] == "7" or word[:i] == "07":
                            new_words.append("july")
                        elif word[:i] == "8" or word[:i] == "08":
                            new_words.append("august")
                        elif word[:i] == "9" or word[:i] == "09":
                            new_words.append("september")
                        elif word[:i] == "10":
                            new_words.append("october")
                        elif word[:i] == "11":
                            new_words.append("november")
                        elif word[:i] == "12":
                            new_words.append("december")
                        month = False
                        day = True
            else:
                for i in range(len(word)):
                    if word[i] == "/":
                        temp1 = num2words(word[:i])
                        temp2 = temp1.replace('-', ' ')
                        temp3 = nltk.word_tokenize(temp2)
                        for w in temp3: new_words.append(w)
                        new_words.append('over')
                        temp1 = num2words(word[i+1:])
                        temp2 = temp1.replace('-', ' ')
                        temp3 = nltk.word_tokenize(temp2)
                        for w in temp3: new_words.append(w)
        else:
            temp1 = num2words(word)
            temp2 = temp1.replace('-', ' ')
            # add the return of that to final
            temp3 = nltk.word_tokenize(temp2)
            for w in temp3: new_words.append(w)

        return new_words

    def money_to_words(self, word: str):
        temp = ''
        final = []
        decimaltag = False
        for d in word:
            if d.isdigit():
                temp = temp + d
            elif d == '.':
                decimaltag = True
                # if temp is empty add 0 to  temp
                if len(temp) != 0:
                    # send the tempStr to be converted to written numbers
                    temp1 = num2words(temp)
                    temp2 = temp1.replace('-', ' ')
                    # add the return of that to final
                    temp3 = nltk.word_tokenize(temp2)
                    for w in temp3: final.append(w)
                    # add 'point' to the final
                    final.append('dollars')
                    final.append('and')
                    # clear temp
                    temp = ''
        if len(temp) != 0:
            temp1 = num2words(temp)
            temp2 = temp1.replace('-', ' ')
            temp3 = nltk.word_tokenize(temp2)
            for w in temp3: final.append(w)
            if decimaltag:
                final.append('cents')
            else:
                final.append('dollars')

        return final

    def time_to_words(self, word: str):
        temp = ''
        final = []
        if len(word) == 3:
            temp1 = num2words(word[0])
            temp2 = temp1.replace('-', ' ')
            temp3 = nltk.word_tokenize(temp2)
            for w in temp3: final.append(w)
            final.append('over')
            temp1 = num2words(word[2])
            temp2 = temp1.replace('-', ' ')
            # add the return of that to final
            temp3 = nltk.word_tokenize(temp2)
            for w in temp3: final.append(w)
            return final
        for d in word:
            if d.isdigit():
                temp = temp + d
            elif d == ':':
                temp1 = num2words(temp)
                temp2 = temp1.replace('-', ' ')
                # add the return of that to final
                temp3 = nltk.word_tokenize(temp2)
                for w in temp3: final.append(w)
                temp = ''
        if len(temp) != 0:
            temp1 = num2words(temp)
            temp2 = temp1.replace('-', ' ')
            temp3 = nltk.word_tokenize(temp2)
            for w in temp3: final.append(w)
        return final

    def percent_to_words(self, word: str):
        temp = ''
        final = []
        for d in word:
            if d.isdigit():
                temp = temp + d
            elif d == '.':
                # if temp is empty add 0 to  temp
                if len(temp) == 0:
                    temp = '0'
                # send the tempStr to be converted to written numbers
                temp1 = num2words(temp)
                temp2 = temp1.replace('-', ' ')
                # add the return of that to final
                temp3 = nltk.word_tokenize(temp2)
                for w in temp3: final.append(w)
                # add 'point' to the final
                final.append('point')
                # clear temp
                temp = ''
        if len(temp) != 0:
            if len(temp) == 1:
                temp = temp + '0'
            temp1 = num2words(temp)
            temp2 = temp1.replace('-', ' ')
            temp3 = nltk.word_tokenize(temp2)
            for w in temp3: final.append(w)
            final.append('percent')

        return final

    # def fraction_to_words(word: str):
