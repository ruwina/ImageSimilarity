import sys
import csv
import fnmatch
import urllib
import os
from os import path
import scipy as sp
import constants
from scipy.misc import imread
from scipy.signal.signaltools import correlate2d as c2d
from PIL import Image
from Tkinter import Tk
from tkFileDialog import askopenfilename
import tkMessageBox
import logging
import time
format= '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s() - %(message)s'
format= '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=format)
logger = logging.getLogger(__name__)


def getLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)

    return logger

log=getLogger()

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


def image_similarity_bands_via_numpy(filepath1, filepath2):
    import math
    import operator
    import numpy
    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)

    # create thumbnails - resize em
    image1 = get_thumbnail(image1)
    image2 = get_thumbnail(image2)

    # this eliminated unqual images - though not so smarts....
    if image1.size != image2.size or image1.getbands() != image2.getbands():
        return -1
    s = 0
    for band_index, band in enumerate(image1.getbands()):
        m1 = numpy.array([p[band_index] for p in image1.getdata()]).reshape(*image1.size)
        m2 = numpy.array([p[band_index] for p in image2.getdata()]).reshape(*image2.size)
        s += numpy.sum(numpy.abs(m1-m2))
    log.info("Completed Bands_Numpy")
    return s

def image_similarity_histogram_via_pil(filepath1, filepath2):
    from PIL import Image
    import math
    import operator

    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)

    image1 = get_thumbnail(image1)
    image2 = get_thumbnail(image2)

    h1 = image1.histogram()
    h2 = image2.histogram()
    try:
        rms = math.sqrt(reduce(operator.add,  list(map(lambda a,b: (a-b)**2, h1, h2)))/len(h1) )
    except (RuntimeError, TypeError, NameError):
        print filepath1
        print h1
        print filepath2
        print h2
        exit()
    return rms

def image_similarity_vectors_via_numpy(filepath1, filepath2):
    # source: http://www.syntacticbayleaves.com/2008/12/03/determining-image-similarity/
    # may throw: Value Error: matrices are not aligned .
    import Image
    from numpy import average, linalg, dot
    import sys

    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)

    image1 = get_thumbnail(image1, stretch_to_fit=True)
    image2 = get_thumbnail(image2, stretch_to_fit=True)

    images = [image1, image2]
    vectors = []
    norms = []
    for image in images:
        vector = []
        for pixel_tuple in image.getdata():
            vector.append(average(pixel_tuple))
        vectors.append(vector)
        norms.append(linalg.norm(vector, 2))
    a, b = vectors
    a_norm, b_norm = norms
    # ValueError: matrices are not aligned !
    res = dot(a / a_norm, b / b_norm)
    return res

def image_similarity_greyscale_hash_code(filepath1, filepath2):
    # source: http://blog.safariflow.com/2013/11/26/image-hashing-with-python/

    image1 = Image.open(filepath1)
    image2 = Image.open(filepath2)

    image1 = get_thumbnail(image1, greyscale=True)
    image2 = get_thumbnail(image2, greyscale=True)

    code1 = image_pixel_hash_code(image1)
    code2 = image_pixel_hash_code(image2)
    # use hamming distance to compare hashes
    res = hamming_distance(code1,code2)
    return res

def image_pixel_hash_code(image):
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join(map(lambda pixel: '1' if pixel < avg else '0', pixels))  # '00010100...'
    hexadecimal = int(bits, 2).__format__('016x').upper()
    return hexadecimal

def hamming_distance(s1, s2):
    len1, len2= len(s1),len(s2)
    if len1!=len2:
        "hamming distance works only for string of the same length, so i'll chop the longest sequence"
        if len1>len2:
            s1=s1[:-(len1-len2)]
        else:
            s2=s2[:-(len2-len1)]
    assert len(s1) == len(s2)
    return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])

def get_thumbnail(image, size=(128,128), stretch_to_fit=False, greyscale=False):
    " get a smaller version of the image - makes comparison much faster/easier"
    if not stretch_to_fit:
        image.thumbnail(size, Image.ANTIALIAS)
    else:
        image = image.resize(size); # for faster computation
    if greyscale:
        image = image.convert("L")  # Convert it to grayscale.
    return image

#write the image not found url and key to csv file
def imgNotFound(key,fileurl):
    try:
        os.makedirs(os.path.dirname(os.getcwd() + constants.IMG_NOT_FOUND_OUTPUT))
    except OSError as e:
        if e.errno != 17:
            raise
            # time.sleep might help here
        pass
    resultarray = [key, fileurl]
    with open(os.getcwd() + constants.IMG_NOT_FOUND_OUTPUT, "a") as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(resultarray)

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


def compare_images(image1, image2):
    resize(image1,image2)
    data1 = imread(image1)
    data2 = imread(image2)
    data1 = conv_to_gray(data1)
    data2 = conv_to_gray(data2)
    finalOutput = calc_similarity(data1,data2)
    log.info("Completed PH")
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
    log.info(message)

def passparameters(arguments,num):
    sys = arguments.split(" ")
    if (len(sys) >= 12):
        if sys[0].startswith('-k'):
            key = sys[1]
        else:
            showDialogBox('Key Missing in line ' + ''.join(num))
        if sys[2].startswith('-u1'):
            url1 = sys[3]
        else:
            showDialogBox('URL missing in line ' + ''.join(num))
        if sys[4].startswith('-u2'):
            url2 = sys[5]
        else:
            showDialogBox('URL missing in line ' + ''.join(num))
        if sys[6].startswith('-f1'):
            file1 = sys[7]
        else:
            showDialogBox('File name missing in line ' + ''.join(num))
        if sys[8].startswith('-f2'):
            file2 = sys[9]
        else:
            showDialogBox('File name missing in line ' + ''.join(num))
        if sys[10].startswith('-o'):
            output = sys[11]
        else:
            showDialogBox('Output File name missing in line ' + ''.join(num))
    # else:
    #     print ('Parameters missing in line ' + ''.join(num))
        if(file1 == '404' or file1 is None):
            imgNotFound(key, file1)
        elif(file2 == '404' or file2 is None):
            imgNotFound(key, file2)
        result1 = isMatch(file1)
        result2 = isMatch(file2)
        if(result1 and result2):
            t1 = time.time()
            result_ph = compare_images(result1,result2)
            duration_for_ph = "%0.1f" % ((time.time() - t1) * 1000)

            # t1 = time.time()
            # result_bands_numpy = image_similarity_bands_via_numpy(result1, result2)
            # duration_for_bands_numpy = "%0.1f" % ((time.time() - t1) * 1000)
            #
            # t1 = time.time()
            # result_histogram_pil = image_similarity_histogram_via_pil(result1, result2)
            # duration_for_histogram_pil = "%0.1f" % ((time.time() - t1) * 1000)
            #
            # t1 = time.time()
            # result_vector_numpy = image_similarity_vectors_via_numpy(result1, result2)
            # duration_for_vector_numpy = "%0.1f" % ((time.time() - t1) * 1000)
            #
            # t1 = time.time()
            # result_greyscale_hash = image_similarity_greyscale_hash_code(result1, result2)
            # duration_for_greyscale_hash = "%0.1f" % ((time.time() - t1) * 1000)
            #
            # result_array = [url1, url2, 'unknwn', 'unknwn',result_bands_numpy, duration_for_bands_numpy,
            #            result_histogram_pil, duration_for_histogram_pil,
            #            result_vector_numpy, duration_for_vector_numpy,
            #            result_greyscale_hash, duration_for_greyscale_hash]
            result_array = [url1, url2, result_ph, duration_for_ph ]
            writeToCSV(key,result_array, output)
        # writeToCSV(key, matchResult2,output)
    # elif not result1:
    #     imgNotFound(key,file1)
    # else:
    #     imgNotFound(key,file2)


def main():
    log.info("START.")
    rootTk = Tk()
    rootTk.withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = 'opwidurl.txt'#askopenfilename() # show an "Open" dialog box and return the path to the selected file
    lines = []
    if(filename):
        with open(filename) as f:
            for num,line in enumerate(f,1):
                 passparameters("".join(line.rstrip('\n')), num)
    showDialogBox("Output written to output file")
    exit()

if __name__ == '__main__':
  main()