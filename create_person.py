#!/usr/bin/python3
import os
import argparse
import time
import sys
from config import config
from termcolor import colored
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, QualityForRecognition, PersonGroup
from azure.cognitiveservices.vision.face.models._models_py3 import APIErrorException
from msrest.exceptions import ValidationError


# Endpoint and Key located in config.py
KEY = config["KEY"]
ENDPOINT = config["ENDPOINT"]
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
accepted_extensions = ["jpg", "png", "jpeg", "bmp", "webp", "gif"]
global intFileIndex
intFileIndex = 0

parser = argparse.ArgumentParser(description='Find face matches from one image.')
parser.add_argument('target_path', type=str,
                    help='path of the image you want to use as a person')
parser.add_argument('--name', type=str, required=True,
                    help='name of the PersonGroup')
parser.add_argument('--person-name', dest='person_name', type=str, required=True,
                    help='name of the Person')
parser.add_argument('--detection-model', dest='detection_model', type=str,
                    default='detection_03',
                    help='detection model for Microsoft Azure. Default is detection_03')
parser.add_argument('--recognition-model', dest='recognition_model', type=str,
                    default='recognition_04',
                    help='recognition model for Microsoft Azure. Default is recognition_04')
parser.add_argument('--paid', dest='paid_version', action="store_true",
                    help='You have the paid version of Azure. This will turn off the time.sleep required for free version. FAST.')
parser.add_argument('-d', '--delete', dest='is_delete', action="store_true",
                    help='You want to overwrite a pre-existing PersonGroup.')

args = parser.parse_args()

def getImageFilesFromDirectory():
  arPossibleImages = [fn for fn in os.listdir(args.target_path) if fn.split(".")[-1] in accepted_extensions]
  if (intFileIndex != 0):
    arPossibleImages = arPossibleImages[intFileIndex:len(arPossibleImages)]
  return arPossibleImages

def createPersonGroup():
  try:
    face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID, recognition_model=args.recognition_model)
  except ValidationError as validationError:
      print(colored('Error for PersonGroup Name Field: {}'.format(validationError), 'red'))
      exit()
  except APIErrorException as apiError:
      print(colored(apiError.message + ' Use the -d delete option to delete existing PersonGroup and create new one.', 'red'))
      exit()

def deletePersonGroup():
  try:
    face_client.person_group.delete(PERSON_GROUP_ID)
  except ValidationError as validationError:
      print(colored('Error for PersonGroup Name Field: {}'.format(validationError), 'red'))
      exit()

PERSON_GROUP_ID = args.name #tornado_project
print('Person group:', PERSON_GROUP_ID)

if (args.is_delete):
  deletePersonGroup()

createPersonGroup()
person = face_client.person_group_person.create(PERSON_GROUP_ID, args.person_name, args.person_name)


for image in getImageFilesFromDirectory():
    ch = open(os.path.join(args.target_path, image), 'r+b')
    sufficientQuality = True
    detected_faces = face_client.face.detect_with_stream(ch, detection_model=args.detection_model, recognition_model=args.recognition_model, return_face_attributes=['qualityForRecognition'])
    '''for face in detected_faces:
        if face.face_attributes.quality_for_recognition != QualityForRecognition.medium:
            sufficientQuality = False
            print('quality not good')
            break
    if not sufficientQuality: continue'''
    face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, person.person_id, open(os.path.join(args.target_path, image), 'r+b'), detection_model=args.detection_model)

print('Training the PersonGroup...')
face_client.person_group.train(PERSON_GROUP_ID)
while (True):
    training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        print(colored('Training Succeeded!!', 'green'))
        break
    elif (training_status.status is TrainingStatusType.failed):
        face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
        sys.exit(colored('Training the Person Group has failed.', 'red'))
    time.sleep(5)