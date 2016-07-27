from src.image_processing.impros_conf import CONFIG
import src.image_processing.impros as impros
from sklearn.externals import joblib
import matplotlib.pyplot as plt
from skimage import feature
import numpy as np
import shutil
import cv2
import csv
import os

def scan_img(path=None, link=None):
    """
        get ONE face
        GET eye rect
        approximate nose location
        rescale and crop everything

        calc DAISY descr for each image
        cluster descriptors with hierarchical clustering
        make BoW
        feed SVM
    """

    img = cv2.imread(path, 0)
    face = impros.detect_face(img=img)
    if len(face) == 0:
        print('No face found')
        os.remove(path)
        return None

    x,y,w,h = face
    face_img = img[y:y+h, x:x+w]

    eyes_rect = impros.detect_eyes(face_img, CONFIG['haar_conf']['eye_clf'])
    rect_is_found=True
    if len(eyes_rect) == 0:
        # print('Eye rectangle not found')
        eyes_rect = impros.detect_eyes(face_img, CONFIG['haar_conf']['eye_clf1'])
        rect_is_found=False
        if len(eyes_rect) != 2:
            # print('Eyes not detected correctly')
            os.remove(path)
            return None

    if rect_is_found:
        eyes_rect = eyes_rect[0]
    else:
        leye = eyes_rect[0] if eyes_rect[0][0] < eyes_rect[1][0] else eyes_rect[1]
        reye = eyes_rect[1] if eyes_rect[0][0] < eyes_rect[1][0] else eyes_rect[0]
        x = leye[0]
        miny = min(leye[1], reye[1])
        maxy = max(leye[1], reye[1])
        width = abs(reye[0] + reye[2] - leye[0])
        _height = leye[3] if leye[1] == maxy else reye[3]
        height = maxy + _height - miny
        eyes_rect = (x, miny, width, height)

    x,y,w,h = eyes_rect
    # print('Eyes rect:', eyes_rect)
    left_eye = face_img[y:y+h, x:x+w/2]
    right_eye = face_img[y:y+h, x+w/2:x+w]

    # fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)
    # ax1.imshow(left_eye, cmap='gray')
    # ax2.imshow(right_eye, cmap='gray')
    # plt.show()

    nose_obj = impros.detect_nose(face_img, eyes_rect)
    if nose_obj is None:
        os.remove(path)
        return;
    x,y,w,h,angle = nose_obj
    nose_img = impros.rotate_img(face_img, angle)[y:y+h, x:x+w]
    # cv2.imshow('img', nose_img)
    # cv2.waitKey(0)
    # os.remove(path)

    face_img = impros.resize_img(face_img, CONFIG['daisy_conf']['face_size'])
    left_eye = impros.resize_img(left_eye, CONFIG['daisy_conf']['le_size'])
    right_eye = impros.resize_img(right_eye, CONFIG['daisy_conf']['re_size'])
    nose_img = impros.resize_img(nose_img, CONFIG['daisy_conf']['nose_size'])


    face_daisy = feature.daisy(face_img, step=8, radius=24, rings=3, histograms=6,
    orientations=8)
    le_daisy = feature.daisy(left_eye, step=8, radius=16, rings=3, histograms=6,
    orientations=8)
    re_daisy = feature.daisy(right_eye, step=8, radius=16, rings=3, histograms=6,
    orientations=8)
    nose_daisy = feature.daisy(nose_img, step=8, radius=12, rings=3, histograms=6,
    orientations=8)

    print('shapes:', face_daisy.shape, le_daisy.shape, re_daisy.shape, nose_daisy.shape)

    def write_csv(postfix, data, user_id):
        with open('src/image_processing/data/daisy/data_daisy_'+postfix+'.csv', 'a+') as csvfile:
            writer = csv.writer(csvfile, strict=True)
            for x in range(data.shape[0]):
                for y in range(data.shape[1]):
                    writer.writerow(np.append(data[x,y], [user_id]))

    user_id = path.split('/')[-2]
    # print(user_id)
    write_csv('face', face_daisy, user_id)
    write_csv('le', le_daisy, user_id)
    write_csv('re', re_daisy, user_id)
    write_csv('nose', nose_daisy, user_id)


def prep_data_daisy(root):
    for dir in os.listdir(root):
        if os.path.isdir(root+'/'+dir) and len(os.listdir(root+'/'+dir)) >= 5:
            for fn in os.listdir(root+'/'+dir):
                path = root+'/'+dir+'/'+fn
                if os.path.isfile(path):
                    # print(path)
                    scan_img(path)


path = 'src/image_processing/photos'
prep_data_daisy(path)