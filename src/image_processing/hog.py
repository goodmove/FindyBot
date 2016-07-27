from src.image_processing.impros_conf import CONFIG
import src.image_processing.impros as impros
from sklearn.externals import joblib
from skimage import feature
import numpy as np
import shutil
import cv2
import csv
import os

"""
    data preparation functions
"""

def compute_hog(img):
    return feature.hog(
                    img,
                    orientations=CONFIG['hog_conf']['orientations'],
                    pixels_per_cell=CONFIG['hog_conf']['pixels_per_cell'],
                    cells_per_block=CONFIG['hog_conf']['cells_per_block'],
                    transform_sqrt=CONFIG['hog_conf']['transform_sqrt']
                    )

def add_hog_feature(img, user_id, csvfile):
    """
        @descr:
            adds a HOG object-feature vector with class label into csv file
    """
    # get HOG descriptor feature vector
    try:
        vector = compute_hog(img)
    except:
        print('File: prep_data_hog.py')
        print('Error while extracting HOG feature vector.')
        return;

    # turn vector into csv formated string
    writer = csv.writer(csvfile, strict=True)
    writer.writerow(np.append(vector, [user_id]))

def breed_images(path, face_rect, randomize, csvfile):
    """
        @descr:
            takes an image, crops it, shifts and reflects `num_of_shifts` times
    """
    img = cv2.imread(path, 0)
    if img is None:
        print('Couldn\'t open img. Path: ', path)
        return;

    resize_values = CONFIG['hog_conf']['resize_values']
    x,y,w,h,dx,dy = face_rect

    for n in range(num_of_shifts):
        shifted = impros.shift_img(img, (x,y,w,h), (dx,dy), randomize=randomize)
        resized = impros.resize_img(shifted, resize_values)
        mirrored = impros.mirror_img(resized)

        # retrieve feature vector and append it to csv file
        add_hog_feature(resized, user_id, csvfile)
        add_hog_feature(mirrored, user_id, csvfile)

def prep_data(root, randomize=True):
    """
        @descr:
            applies a function to each image in each folder in `root` directory
    """

    hog_data_path = CONFIG['data']['hog_data_path']
    if os.path.isfile(hog_data_path):
        os.remove(hog_data_path)

    with open(hog_data_path, 'a') as csvfile:
        for dir in os.listdir(root):
            if os.path.isdir(root+'/'+dir):
                for fn in os.listdir(root+'/'+dir):
                    path = root+'/'+dir+'/'+fn
                    if os.path.isfile(path) and '_' not in fn:
                        face = impros.detect_faces(path=path, count=1)
                        if len(face) > 0:
                            face = impros.extend(face[0], path=path)
                            breed_images(path, face, randomize, csvfile)
                        else:
                            print('hog.py: No face found')
                            os.remove(path)

def predict(path=None, link=None):
    """
        given an image, makes predictions on user_id using HOG features extractor
    """
    print('Predicting HOG...')
    faces = impros.detect_faces(path)
    # faces = impros.get_faces_facerect(link=link, filename=path)
    print(faces)
    if len(faces) == 0:
        return []

    svm_hog_clf = joblib.load(CONFIG['clf_svm']['svm_hog_clf_path'])
    print('classifier loaded')
    ids = []
    for face in faces:
        # x,y,w,h = face['x'], face['y'], face['width'], face['height']
        x,y,w,h = face[:4]
        face_img = cv2.imread(path, 0)
        face_img = impros.resize_img(face_img[y:y+h, x:x+w], CONFIG['hog_conf']['resize_values'])
        hog_feature = compute_hog(face_img)
        id = -1;
        try:
            id = svm_hog_clf.predict(hog_feature.reshape(1,-1))
        except:
            print('Error while extracting HOG feature vector')
            continue
        ids.append(id)
    return ids

