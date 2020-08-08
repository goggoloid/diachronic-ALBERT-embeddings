import os
import pickle
import subprocess
import re

from shutil import copyfile


dir = '/home/ayan-yue/Documents/projects/web-crawlers/national_archives/national_archives'
pdfs_path = dir + '/pdfs'
pdfs_dec_path = dir + '/pdfs_dec'
genre_list_path = dir + '/genre_list'

chunk_range = 100
sent_range = 3

forbidden = ['surveyor', 'surveying']

years = ['2000', '2001', '2002', '2004',
         '2005', '2006', '2007', '2008',
         '2009', '2010', '2011', '2012',
         '2013', '2014', '2015', '2016',
         '2017', '2018', '2019', '2020']

with open(genre_list_path, 'rb') as f:
    genres = pickle.load(f)

print(genres)


    #decrypt
if not os.path.exists(pdfs_dec_path):
    os.makedirs(pdfs_dec_path)

    for file in os.scandir(pdfs_path):

        dec_file = pdfs_dec_path + '/' + os.path.basename(file.path).split('.')[0] + '_dec.pdf'
        subprocess.call(['qpdf', '--decrypt', file.path, dec_file])
        print(dec_file + ' decrypted.')

    #sort
genres_path = dir + '/genres_nat'
if not os.path.exists(genres_path):
    os.makedirs(genres_path)

patterns = '[^A-Za-z0-9.]+'
remove = re.compile(patterns)

for file in os.scandir(pdfs_dec_path):

    subprocess.call(['qpdf', file.path, '--pages', file.path, '1', '--', dir + '/first_page.pdf'])
    subprocess.call(['pdftotext', dir + '/first_page.pdf'])
    with open(dir + '/first_page.txt', 'r', encoding='utf8', errors='ignore') as doc:

        string = doc.read()

    text = re.sub(remove, ' ', string)

    chunks = text.split(' ')[:chunk_range]
    sentences = text.split('.')[:sent_range]

    year = ''
    if any(y in file.path for y in years):

        y_list = [y in file.path for y in years]
        y_in_file = [years[i] for i, _ in enumerate(y_list) if y_list[i]]
        if len(y_in_file) >= 1:
            year = max(y_in_file)

    else:

        for chunk in chunks:

            y_list = [year in chunk for year in years]
            y_in_chunk = [years[i] for i, _ in enumerate(y_list) if y_list[i]]
            if len(y_in_chunk) >= 1:
                year = max(y_in_chunk)
                break

    for sentence in sentences:
        for genre in genres:

            if not any(item in sentence for item in forbidden) and any(item in sentence for item in genre) \
            or not any(item.upper() in sentence for item in forbidden) and any(item.upper() in sentence for item in genre) \
            or not any(item.capitalize() in sentence for item in forbidden) and any(item.capitalize() in sentence for item in genre) \
            or not any(item.title() in sentence for item in forbidden) and any(item.title() in sentence for item in genre):

                genre_in_sent = True

                genre_path = genres_path + '/' + genre[0] + '/' + year
                if not os.path.exists(genre_path):
                    os.makedirs(genre_path)

                genre_text_path = genres_path + '/' + genre[0] + '_texts'
                if not os.path.exists(genre_text_path):
                    os.makedirs(genre_text_path)

                subprocess.call(['pdftotext', file.path])
                name = os.path.basename(file.path).split('.')[0]

                if year != '':

                    copyfile(file.path, genre_path + '/' + year + '-' + os.path.basename(file.path))
                    os.rename(pdfs_dec_path + '/' + name + '.txt', genre_text_path + '/' + year + '-' + name + '.txt')

                else:

                    if not os.path.exists(genre_text_path + '/undated'):
                        os.makedirs(genre_text_path + '/undated')

                    undated_path = genres_path + '/' + genre[0] + '/undated'
                    if not os.path.exists(undated_path):
                        os.makedirs(undated_path)

                    copyfile(file.path, undated_path + '/' + os.path.basename(file.path))
                    os.rename(pdfs_dec_path + '/' + name + '.txt', genre_text_path + '/undated' + '/' + year + '-' + name + '.txt')

                print(os.path.basename(file.path) + ' sorted.')

            else:

                genre_in_sent = False

            if genre_in_sent:
                break

        if genre_in_sent:
            break


os.remove(dir + '/first_page.pdf')
os.remove(dir + '/first_page.txt')
