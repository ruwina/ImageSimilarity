import sys
import csv
import fnmatch
import os
from os import path
import scipy as sp
from scipy.misc import imread
from scipy.signal.signaltools import correlate2d as c2d
from PIL import Image
from Tkinter import Tk
from tkFileDialog import askopenfilename
import tkMessageBox

#converting RGB to grayscale
def conv_to_gray(image):
    return sp.inner(image, [0.299, 0.587, 0.114])

#resize the larger image to smaller image size
def resize(image1, image2):
    d1img = Image.open(image1)
    d2img = Image.open(image2)
    ht1, wd1 = d1img.size
    ht2, wd2 = d2img.size
    if ((ht1, wd1) != (ht2, wd2)):
        if ((ht1, wd1) > (ht2, wd2)):
            modIm = d1img.resize((ht2, wd2) , Image.ANTIALIAS)
            modIm.save(image1)
        else:
            modIm = d2img.resize((ht1, wd1) , Image.ANTIALIAS)
            modIm.save(image2)

def calc_similarity(data1, data2):
    output1 = (data1 - data1.mean()) / data1.std()
    output2 = (data2 - data2.mean()) / data2.std()
    op11 = c2d(output1, output1, mode="same")
    op12 = c2d(output1, output2, mode='same')
    finalOutput = (op12.max() / op11.max()) * 100
    return finalOutput

#write the output to csv file
def writeToCSV(key,resultarray,outputFile):
    resultarray = [key] + resultarray
    try:
        os.makedirs(os.path.dirname(outputFile))
    except OSError as e:
        if e.errno != 17:
            raise
            # time.sleep might help here
        pass
    with open(outputFile, "a") as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(resultarray)

def compare_images(image1, image2):
    resize(image1,image2)
    data1 = imread(image1)
    data2 = imread(image2)
    data1 = conv_to_gray(data1)
    data2 = conv_to_gray(data2)
    finalOutput = calc_similarity(data1,data2)
    resultArray = [image1,image2,"{0:.2f}".format(finalOutput)]
    return resultArray

#returns full file path if file exists in the directory
#
def isMatch(filepath):
    if os.path.exists(filepath):
        return os.path.join(" ",filepath)
    else:
        return False

def showDialogBox(message):
    root = Tk()
    root.withdraw()
    tkMessageBox.showinfo("Message", message)
    root.mainloop()

def passparameters(arguments,num):
    sys = arguments.split(" ")
    if (len(sys) >= 8):
        if sys[0].startswith('-k'):
            key = sys[1]
        else:
            showDialogBox('Key Missing in line ' + ''.join(num))
        if sys[2].startswith('-f1'):
            file1 = sys[3]
        else:
            showDialogBox('File name missing in line ' + ''.join(num))
        if sys[4].startswith('-f2'):
            file2 = sys[5]
        else:
            showDialogBox('File name missing in line ' + ''.join(num))
        if sys[6].startswith('-o'):
            output = sys[7]
        else:
            showDialogBox('Output File name missing in line ' + ''.join(num))
    else:
        showDialogBox('Parameters missing in line ' + ''.join(num))
    result1 = isMatch(file1)
    result2 = isMatch(file2)
    if(result1 and result2):
        matchResult1 = compare_images(result1,result2)
        matchResult2 = compare_images(result2, result1)
        writeToCSV(key,matchResult1,output)
        writeToCSV(key, matchResult2,output)
    elif not result1:
        showDialogBox('404: File from url1 for key' + key + ' not found error.')
        pass
    else:
        showDialogBox('404: File from url2 for key' + key + ' not found error.')
        pass


def main():
    rootTk = Tk()
    rootTk.withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    lines = []
    if(filename):
        with open(filename) as f:
            for num,line in enumerate(f,1):
                 passparameters("".join(line.rstrip('\n')), num)
    showDialogBox("Output written to output file")
    exit()

if __name__ == '__main__':
  main()