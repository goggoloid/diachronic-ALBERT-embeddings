import os
import shutil

genre_list = ['annual report',
              'consultation',
              'evaluation',
              'impact assessment',
              'survey']

merge_path = '/home/ayan-yue/Documents/projects/merge'

gov_path = merge_path + '/genres_gov'
nat_path = merge_path + '/genres_nat'
paths = [gov_path, nat_path]

merged_path = merge_path + '/genres'
if not os.path.exists(merged_path):
    os.makedirs(merged_path)


for path in paths:

    for file in os.scandir(path):
        for genre in genre_list:

            merged_genre = merged_path + '/' + genre
            if not os.path.exists(merged_genre):
                os.makedirs(merged_genre)

            if os.path.basename(file.path) == genre + '_texts':

                for text in os.scandir(file.path):
                    if os.path.basename(text.path) != 'undated':

                        shutil.copy(text.path, merged_genre + '/' + os.path.basename(text.path))
