#!/usr/bin/python3
# Created By: Amanda Szampias
# Description: Python Script uses Azure FaceAPI to detect and verify faces.
import os
import time
import re
import argparse
import colorama
import shutil
from config import config
from termcolor import colored
from pathlib import Path
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models._models_py3 import APIErrorException

KEY = config["KEY"]
ENDPOINT = config["ENDPOINT"]
MAX_REQUEST_RATE_FREE = config["MAX_REQUEST_FREE_VERSION"]
REQUEST_TIMEOUT_TIME = config["REQUEST_TIMEOUT_TIME"]
accepted_extensions = ["jpg", "png", "jpeg", "bmp", "webp", "gif"]
global intRequestCounter
intRequestCounter = 0
global intTotalRequests
intTotalRequests = 0
global intFileIndex
intFileIndex = 0
global intSuccessMatches
intSuccessMatches = 0
imageCompareDir = os.path.join(os.getcwd(), 'Images')
global dirFoundImages
dirFoundImages = './Found_Images'
endLoop = False

colorama.init()
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

parser = argparse.ArgumentParser(description='Find face matches from one image.')
parser.add_argument('target_resource', type=str,
                    help='path of the image you want found OR provide person_group_id')
parser.add_argument('--detection-model', dest='detection_model', type=str,
                    default='detection_03',
                    help='detection model for Microsoft Azure. Default is detection_03')
parser.add_argument('--recognition-model', dest='recognition_model', type=str,
                    default='recognition_04',
                    help='recognition model for Microsoft Azure. Default is recognition_04')
parser.add_argument('--paid', dest='paid_version', action="store_true",
                    help='You have the paid version of Azure. This will turn off the time.sleep required for free version. FAST.')
parser.add_argument('--max', dest='max_request_limit', type=int,
                    help='Do you want the program to stop at a certain threshold? Ex: 100000 requests')
parser.add_argument('-c', '--compare-directory', dest='compare_directory', type=str, default=None,
                    help='Is there another folder you would like to get comparision images from? Default is Current_Directory/Images/')
parser.add_argument('-o', '--output-file', dest='output_file_name', type=str, default='success.txt',
                    help='Name of the output file. Default is success.txt')
parser.add_argument('-s', '--start-at', dest='start_at', type=int, default=None,
                    help='Need to start at the middle of a directory? Input the file number here. 5 = 5th Image')

args = parser.parse_args()
successFile = open(args.output_file_name,'a')
Path(dirFoundImages).mkdir(parents=True, exist_ok=True)

def setImageComparisionDirectory():
  if (os.path.isdir(args.compare_directory)): 
    return args.compare_directory
  else:
    exit(colored('The directory provided does not exist: ' + args.compare_directory, 'yellow'))

def getImageFilesFromDirectory():
  arPossibleImages = [fn for fn in os.listdir(imageCompareDir) if fn.split(".")[-1] in accepted_extensions]
  if (intFileIndex != 0):
    arPossibleImages = arPossibleImages[intFileIndex:len(arPossibleImages)]
  return arPossibleImages

def openTargetFile():
  try: 
    return open(args.target_resource, 'rb') 
  except:
    exit(colored('Cannot open the target image file: ' + args.target_resource, 'yellow'))

def calculateAPIErrorTimeout(errorMessage):
  querySecond = re.search('after (.*) second', errorMessage)
  if (querySecond != None):
    return int(querySecond.group(1)) + 1
  return 1
  
def checkMaxRequestLimit():
    global intTotalRequests
    intTotalRequests += 1
    if (args.max_request_limit != None):
        if (intTotalRequests > args.max_request_limit):
          print(colored('Max Request Limit has been reached. Total Requests: ' + str(intTotalRequests), 'yellow'))
          exit(colored('Limit Set By User: ' + str(args.max_request_limit), 'yellow'))

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
    global intSuccessMatches
    intSuccessMatches += 1
    successFile.write('Faces from {} & {} are of the same person, with confidence: {}\n'.format(targetImageName, imgPossibleName, faceVerifyResults.confidence))
    successFile.flush()
    shutil.copyfile(os.path.join(imageCompareDir, imgPossibleName), os.path.join(dirFoundImages, imgPossibleName))
  else: 
    print(colored('Faces from {} & {} are of a different person, with confidence: {}'.format(targetImageName, imgPossibleName, faceVerifyResults.confidence), 'red'))

def comparePersonGroupToFace(possibleDetectedFace, imgPossibleName):
  arPersonResults = face_client.face.identify([possibleDetectedFace.face_id], args.target_resource)
  if not arPersonResults:
    print(colored('No person identified in the person group for faces from {}.'.format(imgPossibleName), 'red'))
  for person in arPersonResults:
    if len(person.candidates) > 0:
      personName = face_client.person_group_person.get(args.target_resource, person.candidates[0].person_id).name
      print(colored('Person {} is identified in {} with a confidence of {}.'.format(personName, imgPossibleName, person.candidates[0].confidence), 'green'))
      global intSuccessMatches
      intSuccessMatches += 1
      successFile.write('Person {} is identified in {} with a confidence of {}.\n'.format(personName, imgPossibleName, person.candidates[0].confidence))
      successFile.flush()
      shutil.copyfile(os.path.join(imageCompareDir, imgPossibleName), os.path.join(dirFoundImages, imgPossibleName))
    else:
      print(colored('No person identified in {}.'.format(imgPossibleName), 'red'))

def getPossibleDetectedFaces(imageName):
  imgPossible = open(os.path.join(imageCompareDir, imageName), 'rb') 
  arPossibleDetectedFaces = face_client.face.detect_with_stream(imgPossible, detection_model=args.detection_model, recognition_model=args.recognition_model)
  print('{} face(s) detected from image {}.'.format(len(arPossibleDetectedFaces), imageName))
  return arPossibleDetectedFaces

def checkTargetImageForMultipleFaces(arDetectedFaces):
    if (len(arDetectedFaces) > 1):
      exit(colored('The target image provided has more than 1 face. Please provide an image with only one face.', 'yellow'))
    if (len(arDetectedFaces) < 1):
      exit(colored('Microsoft Azure found 0 faces in this image. Please provide an image with one face', 'yellow'))

def getTargetImageFaceId():
  targetImage = openTargetFile()
  targetImageName = os.path.basename(targetImage.name)
  arDetectedFaces = face_client.face.detect_with_stream(targetImage, detection_model=args.detection_model, recognition_model=args.recognition_model)
  checkTargetImageForMultipleFaces(arDetectedFaces)
  targetImageFaceID = arDetectedFaces[0].face_id
  print('{} face detected from target image {}.'.format(len(arDetectedFaces), targetImageName))
  incrementCounter()
  return targetImageFaceID, targetImageName

def getKeyboardInterruptAction():
  successFile.close()
  print(colored('\nUser Exited Program. Total API Requests Made: {}'.format(intTotalRequests), 'yellow'))
  exit(colored('File Index is at: {}'.format(intFileIndex), 'yellow'))

def getAPIExceptionAction(errorMessage):
  print(errorMessage.message)
  if (errorMessage.message == '(InvalidImage) Resizing image failed, image format not supported.'):
    global intFileIndex
    intFileIndex += 1
  intTimeToSleep = calculateAPIErrorTimeout(errorMessage.message)
  print(colored('File Index is at: {}'.format(intFileIndex), 'yellow'))
  print(colored('Pausing and Resuming in {} seconds...'.format(intTimeToSleep), 'yellow'))
  args.start_at = intFileIndex
  time.sleep(intTimeToSleep)

def checkArgs():
  if (args.compare_directory != None):
    global imageCompareDir
    imageCompareDir = setImageComparisionDirectory()

  if (args.start_at != None):
    global intFileIndex
    intFileIndex = args.start_at

checkArgs()
if ('.' in args.target_resource):
  targetImageFaceID, targetImageName = getTargetImageFaceId()

arImageFiles = getImageFilesFromDirectory()
print('Total Images in Processing: {}'.format(len(arImageFiles)))
while (endLoop == False):
  try:
    for imageName in getImageFilesFromDirectory():
      arPossibleDetectedFaces = getPossibleDetectedFaces(imageName)
      incrementCounter()
      for possibleDetectedFace in arPossibleDetectedFaces:
        if ('.' in args.target_resource):
          compareFaceToFace(possibleDetectedFace, imageName)
        else:
          comparePersonGroupToFace(possibleDetectedFace, imageName)
        incrementCounter()
      intFileIndex += 1
    endLoop=True
    print('{} Images Processed'.format(len(arImageFiles)))
    print('{} Total Faces Matched'.format(intSuccessMatches))
  except APIErrorException as errorMessage:
    getAPIExceptionAction(errorMessage)
    intRequestCounter = 0
  except KeyboardInterrupt:
    getKeyboardInterruptAction()

successFile.close()