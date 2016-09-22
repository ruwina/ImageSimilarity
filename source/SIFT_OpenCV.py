import cv2
import numpy as np
from matplotlib import pyplot as plt

import csv
import os
import logging
from PIL import Image
logging.basicConfig(level=logging.DEBUG, format=format)
logger = logging.getLogger(__name__)

img1 = cv2.imread('./data/814537003003_url1.jpg')
gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
img2 = cv2.imread('./data/814537003003_url2.jpg')
gray2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
sift = cv2.xfeatures2d.SIFT_create()
surf = cv2.xfeatures2d.SURF_create()

(kps_sift_1, descs_sift_1) = sift.detectAndCompute(gray1, None)
(kps_surf_1, descs_surf_1) = surf.detectAndCompute(gray1, None)
(kps_sift_2, descs_sift_2) = sift.detectAndCompute(gray2, None)
(kps_surf_2, descs_surf_2) = surf.detectAndCompute(gray2, None)

#Brute Force Matcher
bf = cv2.BFMatcher(cv2.DIST_L2, crossCheck=True)
origmatch = bf.match(descs_sift_1, descs_sift_1)
lenorig = float(len(origmatch))
matches = bf.match(descs_sift_1, descs_sift_2)
lenmatch = float(len(matches))
percent = lenmatch/lenorig * 100
print(format(percent, '.2f'))

bf = cv2.BFMatcher(cv2.DIST_L2, crossCheck=True)
origsurf = bf.match(descs_surf_1, descs_surf_1)
lenorigsurf = float(len(origsurf))
matchessurf = bf.match(descs_surf_1, descs_surf_2)
lenmatchsurf = float(len(matchessurf))
percentsurf = lenmatchsurf/lenorigsurf * 100
print(format(percentsurf, '.2f'))

matches = sorted(matches, key = lambda x:x.distance)
img3 = cv2.drawMatches(img1,kps_sift_1,img2,kps_sift_2,matches[:100000000],None, flags=2)
plt.imshow(img3),plt.show()

def findMatchPercent(desc1, desc2):
    bf = cv2.BFMatcher(cv2.DIST_L2, crossCheck=True)
    origmatch = bf.match(desc1, desc1)
    lenorig = float(len(origmatch))
    matches = bf.match(desc1, desc2)
    lenmatch = float(len(matches))
    percent = lenmatch/lenorig * 100
    return format(percent, '.4f')


def findAvg(percent1, percent2):
    percent1 = float(percent1)
    percent2 = float(percent2)
    avg = (percent1 + percent2) / float(2)
    return format(avg, '.4f')


def convToGray(image):
    rgb_image = cv2.imread(image)
    gray_image = cv2.cvtColor(rgb_image,cv2.COLOR_BGR2GRAY)
    return gray_image


def getSift(gray_image):
    sift = cv2.xfeatures2d.SIFT_create()
    (kps, descs) = sift.detectAndCompute(gray_image, None)
    return (kps, descs)


def getSurf(gray_image):
    surf = cv2.xfeatures2d.SURF_create()
    (kps, descs) = surf.detectAndCompute(gray_image,None)
    return (kps,descs)


def checkSimilarity(image1, image2):
    avg_match_percent = 0
    try:
        gray_image_1 = convToGray(image1)
        (kps_sift_1, descs_sift_1) = getSift(gray_image_1)
        (kps_surf_1, descs_surf_1) = getSurf(gray_image_1)

        gray_image_2 = convToGray(image2)
        (kps_sift_2, descs_sift_2) = getSift(gray_image_2)
        (kps_surf_2, descs_surf_2) = getSurf(gray_image_2)

        match_percent_sift = findMatchPercent(descs_sift_1, descs_sift_2)
        match_percent_surf = findMatchPercent(descs_surf_1, descs_surf_2)
        avg_match_percent = findAvg(match_percent_sift, match_percent_surf)
    except Exception as e:
        print(e)
    return avg_match_percent


def checkFileExist(file_name):
    if os.path.exists(file_name):
        if(os.stat(os.path.join(" ", file_name)).st_size >= 2):
            return os.path.join(" ", file_name)
    else:
        return False


def resizeImage(image1,image2):
    d1img = Image.open(image1)
    d2img = Image.open(image2)
    ht1, wd1 = d1img.size
    ht2, wd2 = d2img.size
    if ((ht1, wd1) != (ht2, wd2)):
        if ((ht1, wd1) > (ht2, wd2)):
            modIm = d1img.resize((ht2, wd2), Image.ANTIALIAS)
            modIm.save(image1)
        else:
            modIm = d2img.resize((ht1, wd1), Image.ANTIALIAS)
            modIm.save(image2)


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

log = getLogger()


def logMessage(message):
    print(message)

def writeToCSV(key,result_array,output_file):
    resultarray = [key] + result_array
    try:
        os.makedirs(os.path.dirname(output_file))
    except OSError as e:
        if e.errno != 17:
            raise
            # time.sleep might help here
        pass
    with open(output_file, "a") as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(resultarray)


def readArguments(arguments,line_num):
    sys = arguments.split(" ")
    if (len(sys) >= 12):
        if sys[0].startswith('-k'):
            key = sys[1]
        else:
            logMessage('Key Missing in line ' + ''.join(line_num))
        if sys[2].startswith('-u1'):
            url1 = sys[3]
        else:
            logMessage('URL missing in line ' + ''.join(line_num))
        if sys[4].startswith('-u2'):
            url2 = sys[5]
        else:
            logMessage('URL missing in line ' + ''.join(line_num))
        if sys[6].startswith('-f1'):
            file1 = sys[7]
        else:
            logMessage('File name missing in line ' + ''.join(line_num))
        if sys[8].startswith('-f2'):
            file2 = sys[9]
        else:
            logMessage('File name missing in line ' + ''.join(line_num))
        if sys[10].startswith('-o'):
            output = sys[11]
        else:
            logMessage('Output File name missing in line ' + ''.join(line_num))
        isFileFirst = checkFileExist(file1)
        isFileSecond = checkFileExist(file2)
        if(isFileFirst and isFileSecond):
            resizeImage(isFileFirst,isFileSecond)
            similarity_percent = checkSimilarity(isFileFirst, isFileSecond)
            writeToCSV(key,[url1,url2,isFileFirst,isFileSecond,similarity_percent],output)
        else:
            logMessage('File Not Found')
    else:
        logMessage('Parameters Missing')


def main():
    filename = './input.txt' #askopenfilename() # show an "Open" dialog box and return the path to the selected file
    if(filename):
        with open(filename) as f:
            for num,line in enumerate(f,1):
                 readArguments("".join(line.rstrip('\n')), num)

    exit()

if __name__ == '__main__':
  main()


        # kaze = cv2.KAZE_create()
        # (kps, descs) = kaze.detectAndCompute(gray, None)
        # print("# kps: {}, descriptors: {}".format(len(kps), descs.shape))
        # # kp = sift.detect(gray,None)
        # akaze = cv2.AKAZE_create()
        # (kps, descs) = akaze.detectAndCompute(gray, None)
        # print("# kps: {}, descriptors: {}".format(len(kps), descs.shape))
        #
        # brisk = cv2.BRISK_create()
        # (kps, descs) = brisk.detectAndCompute(gray, None)
        # print("# kps: {}, descriptors: {}".format(len(kps), descs.shape))
        # kp = sift.detect(gray1, None)
        # img = cv2.drawKeypoints(gray1, kp)
        # cv2.imwrite('sift_keypoints.jpg', img)

