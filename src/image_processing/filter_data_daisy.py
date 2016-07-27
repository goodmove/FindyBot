from src.image_processing.impros import ImageProcessor as impros
from src.image_processing.clf_constants import CONSTANTS
import shutil
import cv2
import os

def validate_img(path):
    img = cv2.imread(path, 0)
    face = impros.detect_face(img=img)
    if len(face) == 0:
        print('No face found')
        return False

    x,y,w,h = face
    face_img = img[y:y+h, x:x+w]

    eyes_rect = impros.detect_eyes(face_img, CONSTANTS['eye_clf'])
    if len(eyes_rect) == 0:
        print('Eye rectangle not found')
        eyes_rect = impros.detect_eyes(face_img, CONSTANTS['eye_clf1'])
        if len(eyes_rect) != 2:
            print('Eyes not detected correctly')
            return False

    return True

def filter_data(root):
    for dir in os.listdir(root):
        if os.path.isdir(root+'/'+dir) and len(os.listdir(root+'/'+dir)) >= 5:
            for fn in os.listdir(root+'/'+dir):
                path = root+'/'+dir+'/'+fn
                if os.path.isfile(path):
                    if not validate_img(path):
                        os.remove(path)

        else:
            print('to be removed:', root+'/'+dir)
            shutil.rmtree(root+'/'+dir)

path = 'src/image_processing/photos'
filter_data(path)