import subprocess
import os
import shutil

    #requires installing qpdf (http://qpdf.sourceforge.net/) and xpdf tools (https://www.xpdfreader.com/download.html)

startyear = 2010
n = 11
#genre = 'luhmann'
disk = '/home/ayan-yue'
genres_dir = '/Documents/projects/genres'


for genre in os.listdir(disk + genres_dir):

    print('\nConverting files of genre (' + genre + ')...')

    for i in range(n):

        #input and output directories for pdf decryption
        input_dir = disk + genres_dir + '/' + genre + '/' + str(startyear + i)
        output_dir = disk + genres_dir + '/' + genre + '/' + str(startyear + i) + '_dec'

        #date files
        if os.path.exists(input_dir):
            for entry in os.scandir(input_dir):

                old_name = input_dir + '/' + os.path.basename(entry.path)
                new_name = input_dir + '/' + str(startyear + i) + '-' + os.path.basename(entry.path)
                os.rename(old_name, new_name)

        #output directory for final text files
        txt_dir = disk + '/Documents/projects/genres' + '/' + genre + '_texts'

        #decrypt pdfs with qpdf
        if os.path.exists(input_dir):

            for entry in os.scandir(input_dir):

                dec = os.path.splitext(os.path.basename(entry.path))[0]
                dec_path = input_dir + '/' + dec + '_dec.pdf'
                subprocess.call(['qpdf', '--decrypt', entry.path, dec_path])

            #create separate directory for decrypted pdfs
            os.makedirs(output_dir)
            for file in os.listdir(input_dir):

                filename = os.path.join(input_dir, file)

                if filename.endswith('_dec_dec.pdf'):
                    os.remove(filename)

                elif filename.endswith('_dec.pdf'):
                    file_dest = output_dir + '/' + os.path.basename(filename)
                    shutil.move(filename, file_dest)

            #convert decrypted pdfs into txt files with pdftotext
            for entry in os.scandir(output_dir):

                subprocess.call(['pdftotext', entry.path])

            #create separate directory for txt files
            if not os.path.exists(txt_dir):

                os.makedirs(txt_dir)

            for file in os.listdir(output_dir):

                filename = os.path.join(output_dir, file)
                if filename.endswith('_dec.txt'):

                    file_dest = txt_dir

                    if filename.split('/')[-1] not in os.listdir(file_dest):

                        shutil.move(filename, file_dest)

        if os.path.exists(input_dir):
            print(str(startyear + i) + ' completed.')
