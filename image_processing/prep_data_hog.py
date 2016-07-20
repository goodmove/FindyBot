from skimage.transform import pyramid_gaussian
from impros import ImageProcessor as impros
from clf_constants import CONSTANTS
from skimage import feature
import numpy as np
import shutil
import csv
import cv2
import os

"""
    data preparation functions
"""
def add_hog_feature(img, path):
    """
        @descr:
            adds an object-feature vector with class label, copmuted with HOG, into csv file
    """
    # get HOG descriptor feature vector
    try:
        vector = feature.hog(
                        img,
                        orientations=CONSTANTS['orientations'],
                        pixels_per_cell=CONSTANTS['pixels_per_cell'],
                        cells_per_block=CONSTANTS['cells_per_block'],
                        transform_sqrt=CONSTANTS['transform_sqrt']
                        )
    except:
        print('File: prep_data_hog.py')
        print('Error while extracting HOG feature vector.')

    user_id = path.split('/')[-2]
    vector = np.append(vector, [user_id])

    # turn vector into csv formated string
    with open('./data/data_hog.csv', 'a+') as csvfile:
        writer = csv.writer(csvfile, strict=True)
        writer.writerow(vector)

def get_faces(path, faces, shift_values):
    """
        @descr:
            looks for face in the image and returnds its extended rectangle
    """
    img = cv2.imread(path, 0)
    if img is None:
        print('Couldn\'t open img. Path: ', path)
        return faces;

    res = impros.detect_face_ext(bounds=shift_values, img=img)

    if len(res) == 0:
        # remove the original image
        print('No face found')
        os.remove(path)
        return faces;

    faces.append(res)
    return faces

def propagate_images(path, face_rect, num_of_shifts, randomize, resize_values):
    """
        @descr:
            takes an image, crops it, shifts and reflects `num_of_shifts` times
    """
    img = cv2.imread(path, 0)
    if img is None:
        print('Couldn\'t open img. Path: ', path)
        return;

    x,y,w,h,dx,dy = face_rect

    # remove the original image
    # os.remove(path)

    for n in range(num_of_shifts):
        shifted = impros.shift_img(img, (x,y,w,h), (dx,dy), randomize=randomize)
        resized = impros.resize_img(shifted, resize_values)
        mirrored = impros.mirror_img(resized)

        # retrieve feature vector and append it to csv file
        add_hog_feature(resized, path)
        add_hog_feature(mirrored, path)

        """
        !!!
        the following actually turns out to be extra memory usage,
        since we've just computed feature vector and appended it to csv file
        !!!
        """
        # crop face and save it
        cv2.imwrite(path[:-4] + str(n) + '_.jpg', resized)
        cv2.imwrite(path[:-4] + str(n) + '__.jpg', mirrored)

def prep_data_hog(root, num_of_shifts=10, randomize=True, shift_values=None, resize_values=CONSTANTS['resize_values']):
    """
        @descr:
            applies a function to each image in each folder in `root` directory
    """
    for dir in os.listdir(root):
        if os.path.isdir(root+'/'+dir):
            # `faces` is initialized for future extension to multi-detection
            faces = []
            path = ''
            for fn in os.listdir(root+'/'+dir):
                path = root+'/'+dir+'/'+fn
                if os.path.isfile(path) and '_' not in fn:
                    faces = get_faces(path, faces, shift_values)
                    if len(faces) > 0:
                        propagate_images(path, faces.pop(0), num_of_shifts, randomize, resize_values)
