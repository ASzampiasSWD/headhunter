#!/usr/bin/python3
import os
import time
import argparse
from config import config
from termcolor import colored
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

# Endpoint and Key located in config.py
KEY = config["KEY"]
ENDPOINT = config["ENDPOINT"]
MAX_REQUEST_RATE_FREE = config["MAX_REQUEST_FREE_VERSION"]
REQUEST_TIMEOUT_TIME = config["REQUEST_TIMEOUT_TIME"]
accepted_extensions = ["jpg", "png", "jpeg", "bmp", "webp", "tiff", "tif"]
global intRequestCounter
intRequestCounter = 0
global intTotalRequests
intTotalRequests = 0
global intFileIndex
intFileIndex = 0
imageCompareDir = os.path.join(os.getcwd(), 'Images')

successFile = open('success.txt','a')
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

parser = argparse.ArgumentParser(description='Find face matches from one image.')
parser.add_argument('target_file', type=str,
                    help='path of the image you want found')
parser.add_argument('--detection-model', dest='detection_model', type=str,
                    default='detection_03',
                    help='detection model for Microsoft Azure. Default is detection_03')
parser.add_argument('--paid', dest='paid_version', action="store_true",
                    help='You have the paid version of Azure. This will turn off the time.sleep required for free version. FAST.')
parser.add_argument('--max', dest='max_request_limit', type=int,
                    help='Do you want the program to stop at a certain threshold? Ex: 100000 requests')
parser.add_argument('--compare-directory', dest='compare_directory', type=str, default=None,
                    help='Is there another folder you would like to get comparision images from? Default is Current_Directory/Images/')
parser.add_argument('--start-at', dest='start_at', type=int, default=None,
                    help='Need to start at the middle of a directory? Input the file number here. 5 = 5th Image')

args = parser.parse_args()

def setImageComparisionDirectory():
  if (os.path.isdir(args.compare_directory)): 
    return args.compare_directory
  else:
    print(colored('The directory provided does not exist: ' + args.compare_directory, 'yellow'))
    exit()

def getImageFilesFromDirectory():
  arPossibleImages = [fn for fn in os.listdir(imageCompareDir) if fn.split(".")[-1] in accepted_extensions]
  if (args.start_at != None):
    print('Default Array: {}'.format(arPossibleImages))
    arPossibleImages = arPossibleImages[args.start_at:len(arPossibleImages)]
    print('Selected Array with start_at argument: {}'.format(arPossibleImages))
    global intFileIndex
    intFileIndex = args.start_at
  return arPossibleImages

def openTargetFile():
    try: 
        return open(args.target_file, 'rb') 
    except:
        print(colored('Cannot open the target image file: ' + args.target_file, 'yellow'))
        exit()

def checkMaxRequestLimit():
    global intTotalRequests
    intTotalRequests += 1
    if (args.max_request_limit != None):
        if (intTotalRequests > args.max_request_limit):
          print(colored('Max Request Limit has been reached. Total Requests: ' + str(intTotalRequests), 'yellow'))
          print(colored('Limit Set By User: ' + str(args.max_request_limit), 'yellow'))
          exit()

def incrementCounter():
  checkMaxRequestLimit()
  if (args.paid_version == False):
    global intRequestCounter
    intRequestCounter += 1
    runSleepForMaxRequest()

def runSleepForMaxRequest():
    global intRequestCounter
    if (intRequestCounter >= MAX_REQUEST_RATE_FREE):
      print('MAX REQUEST RATE ACHIEVED. STALL {} SECONDS.'.format(REQUEST_TIMEOUT_TIME))
      time.sleep(REQUEST_TIMEOUT_TIME)
      intRequestCounter = 0

def compareFaceToFace(possibleDetectedFace, imgPossibleName):
  faceVerifyResults = face_client.face.verify_face_to_face(targetImageFaceID, possibleDetectedFace.face_id)
  if (faceVerifyResults.is_identical == True):
    print(colored('Faces from {} & {} are of the same person, with confidence: {}'.format(targetImageName, imgPossibleName, faceVerifyResults.confidence), 'green'))
    successFile.write('Faces from {} & {} are of the same person, with confidence: {}\n'.format(targetImageName, imgPossibleName, faceVerifyResults.confidence))
  else: 
    print(colored('Faces from {} & {} are of a different person, with confidence: {}'.format(targetImageName, imgPossibleName, faceVerifyResults.confidence), 'red'))

def getPossibleDetectedFaces(imageName):
  imgPossible = open(os.path.join(imageCompareDir, imageName), 'rb') 
  arPossibleDetectedFaces = face_client.face.detect_with_stream(imgPossible, detection_model=args.detection_model)
  print('{} face(s) detected from image {}.'.format(len(arPossibleDetectedFaces), imageName))
  return arPossibleDetectedFaces

def checkTargetImageForMultipleFaces(arDetectedFaces):
    if (len(arDetectedFaces) > 1):
      print(colored('The target image provided has more than 1 face. Please provide an image with only one face.', 'yellow'))
      exit()
    if (len(arDetectedFaces) < 1):
      print(colored('Microsoft Azure found 0 faces in this image. Please provide an image with one face', 'yellow'))
      exit()

if (args.compare_directory != None):
  imageCompareDir = setImageComparisionDirectory()

targetImage = openTargetFile()
targetImageName = os.path.basename(targetImage.name)
arDetectedFaces = face_client.face.detect_with_stream(targetImage, detection_model=args.detection_model)
checkTargetImageForMultipleFaces(arDetectedFaces)
targetImageFaceID = arDetectedFaces[0].face_id
print('{} face detected from target image {}.'.format(len(arDetectedFaces), targetImageName))
incrementCounter()

try:
  for imageName in getImageFilesFromDirectory():
    arPossibleDetectedFaces = getPossibleDetectedFaces(imageName)
    incrementCounter()
    for possibleDetectedFace in arPossibleDetectedFaces:
      compareFaceToFace(possibleDetectedFace, imageName)
      incrementCounter()
    intFileIndex += 1
except KeyboardInterrupt:
  print(colored('\nUser Exited Program. Total API Requests Made: {}'.format(intTotalRequests), 'yellow'))
  print(colored('File Index is at: {}'.format(intFileIndex), 'yellow'))
  successFile.close()

successFile.close()