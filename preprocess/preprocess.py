import os
import collections
import re
import pickle

from collections import OrderedDict



#preprocess and load data by genre

def preprocess(path, max_char, min_char, patterns, query_words=None, ALL=False):

    d = OrderedDict()

    if len(patterns) > 1:

        remove = re.compile('|'.join(patterns))

    if len(patterns) == 1:

        remove = re.compile(patterns[0])


#    genre_paths = [(file, path + '/' + file) for file in os.listdir(path) if file.endswith('_texts')]
    genre_paths = [(file, path + '/' + file) for file in os.listdir(path)]

    for genre, genre_path in genre_paths:

        d['{}'.format(genre)] = []
        print('Preprocessing genre: ' + genre + '...')

        text_paths = [genre_path + '/' + text for text in os.listdir(genre_path)]
        for text in text_paths:

            with open(text, 'r', encoding='utf8', errors='ignore') as doc:

                string = str(doc.read())
                string = string.split('. ')

                txt_list = [re.sub(remove, ' ', sentence) for sentence in string if len(sentence) <= max_char and len(sentence) >= min_char]
                temp_list = []
                for sentence in txt_list:
                    if '. ' in sentence:

                        split_sent = sentence.split('. ')
                        for sent in split_sent:
                            if sent != '' and len(sent) > 5:

                                temp_list.append(sent)
                    else:

                        temp_list.append(sentence)

                txt_list = temp_list
                for sentence in txt_list:

                    if query_words == None:

                        d[genre].append(sentence)



                    elif type(query_words) == list:

                        if ALL:

                            if all(word in sentence for word in query_words):

                                d[genre].append(sentence)

                        else:

                            if any(word in sentence for word in query_words):

                                d[genre].append(sentence)

                    else:

                        if query_words in sentence:

                            d[genre].append(sentence)

        print('Genre completed.')

    sentences = []
    for genre in d:
        for string in d[genre]:

            sentences.append(string)

    d['all_genres'] = sentences
    print('All genres completed.')

    return d
