import urllib
import os
import constants
from Tkinter import Tk
from tkFileDialog import askopenfilename
import tkMessageBox
import csv

def save_image_details(upc, url1, url2, imagefromfirsturl, imagefromsecondurl):
    if (imagefromfirsturl is False):
        imagefromfirsturl = '404'
    elif (imagefromsecondurl is False):
        imagefromsecondurl = '404'
    outputfilename = "opwidurl.txt"
    text_file = open(os.getcwd() + constants.OUTPUT_DIR + outputfilename, "a")
    outputpath = os.getcwd() + constants.SIMILARITY_CHECK_OUTPUT
    text_file.write("-k %s -u1 %s -u2 %s -f1 %s -f2 %s -o %s\n" % (upc, url1, url2, imagefromfirsturl, imagefromsecondurl, outputpath))
    text_file.close()


def download_photo(img_url, filename):
    try:
        image_on_web = urllib.urlopen(img_url)
        if image_on_web.headers.maintype == 'image':
            buf = image_on_web.read()
            try:
                os.makedirs(os.path.dirname(constants.DOWNLOADED_IMAGE_PATH))
            except OSError as e:
                if e.errno != 17:
                    raise
                    # time.sleep might help here
                pass
            path = os.getcwd() + constants.DOWNLOADED_IMAGE_PATH
            file_path = "%s%s" % (path, filename)
            downloaded_image = file(file_path, "wb")
            downloaded_image.write(buf)
            downloaded_image.close()
            image_on_web.close()
        else:
            return '404'
    except:
        return False
    return file_path


def main():
    rootTk = Tk()
    rootTk.withdraw()
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file

    ifile = open(filename, "rb")
    reader = csv.reader(ifile)

    rownum = 0
    upc = ''
    firsturl = ''
    secondurl = ''
    imagefromfirsturl = ''
    imagefromsecondurl = ''
    for row in reader:
        # Save header row.
        if rownum == 0:
            header = row
        else:
            colnum = 0
            for col in row:
                csvcolheader = header[colnum]

                if(csvcolheader == 'key'):
                    upc = col
                elif (csvcolheader == 'url1'):
                    imagefromfirsturl = download_photo(col.strip('"'),upc+'_url1.jpg')
                    firsturl = col.strip('"')
                elif (csvcolheader == 'url2'):
                    imagefromsecondurl = download_photo(col.strip('"'), upc + '_url2.jpg')
                    secondurl = col.strip('"')
                colnum += 1

            print imagefromsecondurl
            print imagefromfirsturl
            save_image_details(upc, firsturl, secondurl, imagefromfirsturl, imagefromsecondurl)
        rownum += 1

    ifile.close()
    exit()

if __name__ == '__main__':
  main()