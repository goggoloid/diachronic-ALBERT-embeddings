import os
import pickle
import subprocess
import re

from shutil import copyfile

i_dir = '/media/ayan-yue/DATA'
o_dir = '/home/ayan-yue/Documents/projects/web-crawlers/gov/gov'
pdfs_path = i_dir + '/pdfs_gov'
pdfs_dec_path = i_dir + '/pdfs_gov_dec'
genre_list_path = o_dir + '/genre_list.pickle'
forbidden_path = o_dir + '/forbidden.pickle'

sent_range = 10

with open(forbidden_path, 'rb') as f:
    forbidden = pickle.load(f)

with open(genre_list_path, 'rb') as f:
    genres = pickle.load(f)

print(genres)


    #decrypt
if not os.path.exists(pdfs_dec_path):

    os.makedirs(pdfs_dec_path)
    for year in os.scandir(pdfs_path):
        os.makedirs(pdfs_dec_path + '/' + os.path.basename(year.path))

        for pdf in os.scandir(year.path):

            dec_file = pdfs_dec_path + '/' + os.path.basename(year.path) + '/' + os.path.basename(pdf.path).split('.')[0] + '_dec.pdf'
            subprocess.call(['qpdf', '--decrypt', pdf.path, dec_file])
            print(dec_file + ' decrypted.')

    #sort
genres_path = i_dir + '/genres_nat'
if not os.path.exists(genres_path):
    os.makedirs(genres_path)

#patterns = '[^A-Za-z0-9.]+'
#remove = re.compile(patterns)

for y in os.scandir(pdfs_dec_path):
    for file in os.scandir(y.path):

        subprocess.call(['qpdf', file.path, '--pages', file.path, '1', '--', i_dir + '/first_page.pdf'])
        subprocess.call(['pdftotext', i_dir + '/first_page.pdf'])
        with open(i_dir + '/first_page.txt', 'r', encoding='utf8', errors='ignore') as doc:

            text = doc.read()

#        text = re.sub(remove, ' ', string)
        chunks = text.split('.')
        sentences = []
        for chunk in chunks:
            for x in chunk.split('\n'):
                sentences.append(x)

        year = os.path.basename(y.path)

        for sentence in sentences[:sent_range]:
            for genre in genres:

                if not any(item in sentence for item in forbidden[genre[0]]) and any(item in sentence for item in genre) \
                or not any(item.upper() in sentence for item in forbidden[genre[0]]) and any(item.upper() in sentence for item in genre) \
                or not any(item.capitalize() in sentence for item in forbidden[genre[0]]) and any(item.capitalize() in sentence for item in genre) \
                or not any(item.title() in sentence for item in forbidden[genre[0]]) and any(item.title() in sentence for item in genre):

                    genre_in_sentence = True

#                    genre_path = genres_path + '/' + genre[0] + '/' + year
#                    if not os.path.exists(genre_path):
#                        os.makedirs(genre_path)

                    genre_text_path = genres_path + '/' + genre[0] + '_texts'
                    if not os.path.exists(genre_text_path):
                        os.makedirs(genre_text_path)

                    subprocess.call(['pdftotext', file.path])
                    name = os.path.basename(file.path).split('.')[0]

#                    copyfile(file.path, genre_path + '/' + year + '-' + os.path.basename(file.path))
                    if os.path.exists(pdfs_dec_path + '/' + year + '/' + name + '.txt'):
                        os.rename(pdfs_dec_path + '/' + year + '/' + name + '.txt', genre_text_path + '/' + year + '-' + name + '.txt')

                else:

                    genre_in_sentence = False

                if genre_in_sentence:
                    break

            if genre_in_sentence:
                break

if os.path.exists(i_dir + '/first_page.pdf') and os.path.exists(i_dir + '/first_page.txt'):
    os.remove(i_dir + '/first_page.pdf')
    os.remove(o_dir + '/first_page.txt')
